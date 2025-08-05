""" 
Real time STT from microphone using deepgram API:

- capture audio from microphone
- stream over websocket to deepgram
- print finalized transcription in real time

Detailed explanation:
This script captures audio from your microphone, streams it to Deepgram's API over a WebSocket, and prints the transcribed text in real time. It uses asyncio for concurrency, sounddevice for audio input, and websockets for communication.
"""

import os
import asyncio
import json
import sys
from contextlib import suppress
import sounddevice as sd
from websockets.legacy.client import connect
from dotenv import load_dotenv

load_dotenv()

# Load Deepgram API key from .env file
DG_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Audio configuration
SAMPLE_RATE = 16_000
CHUNK_MS = 100
CHUNK_SIZE = SAMPLE_RATE * CHUNK_MS // 1000 # samples per chunk

# Deepgram WebSocket URL with parameters for audio format and transcription options
WS_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=linear16"
    "&sample_rate=16000"
    "&channels=1"
    "&punctuate=true"
    "&interim_results=true"
)

# runs in parallel: captures audio from microphone and puts it into an asyncio queue
async def audio_generator(queue: asyncio.Queue) -> None:
    # This callback is called every CHUNK_MS milliseconds with a chunk of audio data
    def callback(indata, frames, time, status):
        if status:
            print(f"[sounddevice] {status}", file=sys.stderr)
        queue.put_nowait(bytes(indata)) # put bytes into queue

    # Set up the microphone stream
    stream = sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=CHUNK_SIZE,
        dtype="int16",
        channels=1,
        callback=callback,
    )
    stream.start()
    try:
        while True:
            await asyncio.sleep(0.1)  # keep the stream alive
    finally:
        stream.stop()
        stream.close()

# Opens websocket to Deepgram and runs two tasks in parallel: sending audio and receiving transcripts
async def deepgram_loop(queue: asyncio.Queue) -> None:
    async with connect(
        WS_URL,
        extra_headers={"Authorization": f"Token {DG_API_KEY}"},
        ping_interval=5,
        ping_timeout=20,
        close_timeout=0,
    ) as ws:
        print("Listening. Press CTRL+C to stop")
    
        # Create two parallel tasks: one for sending audio, one for receiving transcripts
        send_task = asyncio.create_task(send_audio(ws, queue))
        receive_task = asyncio.create_task(receive_transcripts(ws))

        # Wait until one of the tasks finishes (or errors)
        done, pending = await asyncio.wait(
            {send_task, receive_task},
            return_when=asyncio.FIRST_EXCEPTION,
        )

        # Cancel any pending tasks
        for task in pending:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

# Continuously pull audio chunks from queue and send over websocket to Deepgram
async def send_audio(ws, queue:asyncio.Queue) -> None:
    while True:
        chunk = await queue.get()
        await ws.send(chunk)

# Listen for messages from Deepgram, parse JSON, and print final transcript
async def receive_transcripts(ws) -> None:
    async for message in ws:
        try: 
            data = json.loads(message)

            # Only process final results (not interim)
            if not data.get("speech_final", False) and not data.get("is_final", False):
                continue 
            transcript = (
                data["channel"]["alternatives"][0].get("transcript","")
            )
            if transcript.strip():
                print(transcript)
        except (json.JSONDecodeError, KeyError):
            continue

# Set up asyncio queue and launch audio + websocket tasks
async def main() -> None:
    queue = asyncio.Queue()
    # Start audio capture and Deepgram loop concurrently
    await asyncio.gather(
        audio_generator(queue),
        deepgram_loop(queue),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTranscription stopped.")