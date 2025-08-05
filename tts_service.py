import time
import sys
import os
import subprocess
import platform

# Add the backend directory to Python path to find config module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from groq import Groq

# Initialize the Groq client with your API key from the config module
client = Groq(api_key=config.GROQ_API_KEY)

def text_to_speech(text: str, output_file: str = "speech.wav") -> str:
    """
    Convert text to speech using Groq TTS API
    
    Args:
        text: The text to convert to speech
        output_file: Path where the audio file will be saved
        
    Returns:
        Path to the generated audio file
    """
    # Model and voice settings for Groq TTS
    model = "playai-tts"
    voice = "Mason-PlayAI"
    response_format = "wav"
    
    # Record the start time to measure processing duration
    start_time = time.time()
    
    # Send a request to Groq's TTS API to generate speech from text
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        response_format=response_format
    )
    
    # Record the end time after receiving the response
    end_time = time.time()
    
    # Save the generated audio to a file
    response.write_to_file(output_file)
    
    # Print out how long it took to generate the speech
    print(f"Time to generate voice: {end_time - start_time:.3f} seconds")
    
    return output_file

def play_audio(file_path: str) -> None:
    """
    Play an audio file using system commands
    
    Args:
        file_path: Path to the audio file to play
    """
    try:
        # Determine the operating system to use the appropriate audio player
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # Use afplay (built-in macOS audio player)
            subprocess.run(["afplay", file_path], check=True)
        elif system == "Linux":
            # Use aplay (ALSA audio player for Linux)
            subprocess.run(["aplay", file_path], check=True)
        elif system == "Windows":
            # Use start command to open the audio file with default player
            subprocess.run(["start", file_path], shell=True, check=True)
        else:
            # Fallback for unsupported systems
            print(f"Audio file saved to: {file_path}")
            print("Please play the audio file manually.")
            
    except Exception as e:
        # Handle any errors in audio playback gracefully
        print(f"❌ Error playing audio: {e}")
        print(f"Audio file saved to: {file_path}")

# Example usage when run directly
if __name__ == "__main__":
    # Path where the generated speech audio will be saved
    speech_file_path = "speech.wav"
    # The text you want to convert to speech
    text = "Let me check"
    
    # Convert text to speech
    output_file = text_to_speech(text, speech_file_path)
    
    # Play the generated audio
    play_audio(output_file)