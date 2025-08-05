"""
Configuration file for the Speech Pipeline
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Audio Settings
SAMPLE_RATE = 16000
CHUNK_MS = 100
CHUNK_SIZE = SAMPLE_RATE * CHUNK_MS // 1000

# Deepgram Settings
DEEPGRAM_WS_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=linear16"
    "&sample_rate=16000"
    "&channels=1"
    "&punctuate=true"
    "&interim_results=true"
    "&end_of_speech=3000"
    "&utterance_end_ms=3000"
)

# Groq TTS Settings
TTS_MODEL = "playai-tts"
TTS_VOICE = "Mason-PlayAI"
TTS_FORMAT = "wav"

# Groq LLM Settings
LLM_MODEL = "llama3-8b-8192"
LLM_MAX_TOKENS = 150
LLM_TEMPERATURE = 0.7

# File paths
SPEECH_OUTPUT_FILE = "response.wav" 