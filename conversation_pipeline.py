"""
Conversation Pipeline: Real-time AI Assistant

This module creates a complete conversation pipeline that:
1. Captures speech using Deepgram STT
2. Processes the text through Groq LLM for intelligent responses
3. Converts the response back to speech using Groq TTS
4. Plays the audio response

The pipeline enables real-time conversations with an AI assistant.
"""

import asyncio
import json
import sys
import time
from contextlib import suppress
from typing import Optional

import sounddevice as sd
from websockets.legacy.client import connect
from groq import Groq

import config
from tts_service import text_to_speech

# Initialize Groq client for LLM
llm_client = Groq(api_key=config.GROQ_API_KEY)

class ConversationPipeline:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_listening = True
        self.is_ai_speaking = False  # Flag to track when AI is speaking
        self.conversation_history = []
        self.audio_stream = None  # Store the audio stream for pausing
        self.last_ai_response_time = 0  # Track when AI last responded
        
    async def audio_generator(self) -> None:
        """Capture audio from microphone and put into queue"""
        def callback(indata, frames, time, status):
            if status:
                print(f"[sounddevice] {status}", file=sys.stderr)
            # Only add to queue if AI is not speaking
            if not self.is_ai_speaking:
                self.queue.put_nowait(bytes(indata))
            else:
                # Debug: show when audio is being blocked
                print(f"\r Blocking audio input (AI speaking)", end="", flush=True)

        self.audio_stream = sd.RawInputStream(
            samplerate=config.SAMPLE_RATE,
            blocksize=config.CHUNK_SIZE,
            dtype="int16",
            channels=1,
            callback=callback,
        )
        self.audio_stream.start()
        try:
            while self.is_listening:
                await asyncio.sleep(0.1)
        finally:
            self.audio_stream.stop()
            self.audio_stream.close()

    async def send_audio(self, ws) -> None:
        """Send audio chunks to Deepgram"""
        while self.is_listening:
            chunk = await self.queue.get()
            await ws.send(chunk)

    async def receive_transcripts(self, ws) -> None:
        """Receive and process transcripts from Deepgram"""
        async for message in ws:
            try:
                data = json.loads(message)
                
                # Show interim results for better user feedback
                if data.get("is_final", False) == False and data.get("speech_final", False) == False:
                    # Show interim transcript (optional - for debugging)
                    interim_transcript = data["channel"]["alternatives"][0].get("transcript", "")
                    if interim_transcript.strip():
                        print(f"\r🎤 Speaking: {interim_transcript}", end="", flush=True)
                    continue
                
                # Process final results
                if data.get("speech_final", False) or data.get("is_final", False):
                    transcript = data["channel"]["alternatives"][0].get("transcript", "")
                    
                    if transcript.strip():
                        # Check if this speech came too soon after AI response
                        current_time = time.time()
                        time_since_ai_response = current_time - self.last_ai_response_time
                        
                        if time_since_ai_response < 3.0:  # Ignore speech within 3 seconds of AI response
                            print(f"\n Ignoring speech too soon after AI response: {transcript}")
                            continue
                        
                        print(f"\n You said: {transcript}")
                        
                        # Process the transcript through LLM
                        await self.process_with_llm(transcript)
                    
            except (json.JSONDecodeError, KeyError):
                continue

    async def process_with_llm(self, user_input: str) -> None:
        """Process user input through Groq LLM and generate response"""
        try:
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Create system prompt for the AI assistant
            system_prompt = """You are a helpful AI assistant. Respond naturally and conversationally. 
            Keep your responses concise but informative. Be friendly and engaging."""
            
            # Prepare messages for LLM
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.conversation_history[-6:])  # Keep last 6 messages for context
            
            print("🤔 Thinking...")
            
            # Get response from Groq LLM
            response = llm_client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages,
                max_tokens=config.LLM_MAX_TOKENS,
                temperature=config.LLM_TEMPERATURE,
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            print(f"AI: {ai_response}")
            
            # Convert response to speech
            await self.speak_response(ai_response)
            
        except Exception as e:
            print(f"❌ Error processing with LLM: {e}")
            error_response = "I'm sorry, I encountered an error. Could you please repeat that?"
            await self.speak_response(error_response)

    async def speak_response(self, text: str) -> None:
        """Convert text response to speech and play it"""
        try:
            print("🔊 Converting to speech...")
            
            # Set flag to indicate AI is speaking
            self.is_ai_speaking = True
            self.last_ai_response_time = time.time()
            
            # Generate speech file
            speech_file = text_to_speech(text, config.SPEECH_OUTPUT_FILE)
            
            # Play the audio response
            await self.play_audio_async(speech_file)
            
            # Wait a bit longer to ensure audio is completely finished
            await asyncio.sleep(1.0)
            
            # Reset flag after AI finishes speaking
            self.is_ai_speaking = False
            
            print("✅ Response played")
            print("🎤 Listening for your response...")
            
        except Exception as e:
            print(f"❌ Error in text-to-speech: {e}")
            # Reset flag in case of error
            self.is_ai_speaking = False

    async def play_audio_async(self, file_path: str) -> None:
        """Play audio file asynchronously without blocking the main loop"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            
            if system == "Darwin":  # macOS
                # Use afplay with asyncio subprocess
                process = await asyncio.create_subprocess_exec(
                    "afplay", file_path,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await process.wait()
            elif system == "Linux":
                # Use aplay with asyncio subprocess
                process = await asyncio.create_subprocess_exec(
                    "aplay", file_path,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await process.wait()
            elif system == "Windows":
                # Use start command with asyncio subprocess
                process = await asyncio.create_subprocess_exec(
                    "start", file_path,
                    shell=True,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await process.wait()
            else:
                print(f"Audio file saved to: {file_path}")
                print("Please play the audio file manually.")
                
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
            print(f"Audio file saved to: {file_path}")



    async def deepgram_loop(self) -> None:
        """Main Deepgram WebSocket loop"""
        async with connect(
            config.DEEPGRAM_WS_URL,
            extra_headers={"Authorization": f"Token {config.DEEPGRAM_API_KEY}"},
            ping_interval=5,
            ping_timeout=20,
            close_timeout=0,
        ) as ws:
            print("🎧 Listening for speech. Press CTRL+C to stop")
            print("💡 Speak clearly and wait for the AI to respond")
            
            # Create parallel tasks
            send_task = asyncio.create_task(self.send_audio(ws))
            receive_task = asyncio.create_task(self.receive_transcripts(ws))

            # Wait for tasks to complete
            done, pending = await asyncio.wait(
                {send_task, receive_task},
                return_when=asyncio.FIRST_EXCEPTION,
            )

            # Cancel pending tasks
            for task in pending:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

    async def run(self) -> None:
        """Run the complete conversation pipeline"""
        try:
            await asyncio.gather(
                self.audio_generator(),
                self.deepgram_loop(),
            )
        except KeyboardInterrupt:
            print("\n🛑 Conversation stopped.")
        finally:
            self.is_listening = False

def main():
    """Main entry point for the conversation pipeline"""
    pipeline = ConversationPipeline()
    
    try:
        asyncio.run(pipeline.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 