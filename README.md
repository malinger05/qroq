# Conversation Pipeline: Real-time AI Assistant

A complete conversation pipeline that enables real-time voice conversations with an AI assistant using speech-to-text, Groq LLM processing, and text-to-speech.

## 🎯 Features

- **Real-time Speech Recognition**: Uses Deepgram for accurate speech-to-text conversion
- **Intelligent AI Responses**: Processes speech through Groq LLM for contextual responses
- **Natural Voice Output**: Converts AI responses back to speech using Groq TTS
- **Conversation Memory**: Maintains context across multiple exchanges
- **Error Handling**: Robust error handling for all components

## 📋 Prerequisites

- Python 3.8+
- Microphone access
- Speakers/headphones for audio output
- API keys for Deepgram and Groq

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root with your API keys:

```env
DEEPGRAM_API_KEY=your_deepgram_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Test the Setup

Run the test script to verify all components work:

```bash
python3 test_pipeline.py
```

## 🎮 Usage

### Start a Conversation

```bash
python3 conversation_pipeline.py
```

The system will:
1. Start listening for your voice
2. Convert your speech to text
3. Process it through Groq LLM
4. Generate an AI response
5. Convert the response to speech and play it
6. Repeat the cycle

### Controls

- **Speak clearly** into your microphone
- **Wait for the AI to finish speaking** before speaking again
- **Press Ctrl+C** to stop the conversation

## 📁 File Structure

```
qroq/
├── conversation_pipeline.py  # Main conversation pipeline
├── sst_service.py           # Speech-to-text service (Deepgram)
├── tts_service.py           # Text-to-speech service (Groq)
├── config.py                # Configuration settings
├── test_pipeline.py         # Test script for components
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## ⚙️ Configuration

Edit `config.py` to customize:

- **Audio Settings**: Sample rate, chunk size
- **LLM Settings**: Model, max tokens, temperature
- **TTS Settings**: Voice, model, format
- **File Paths**: Output file locations

## 🔧 Troubleshooting

### Common Issues

1. **Microphone not working**
   - Check microphone permissions
   - Verify microphone is set as default input device

2. **API Key errors**
   - Verify API keys are correctly set in `.env`
   - Check API key validity and quotas

3. **Audio playback issues**
   - Ensure speakers/headphones are connected
   - Check system audio settings

4. **Network connectivity**
   - Verify internet connection for API calls
   - Check firewall settings

### Testing Individual Components

- **STT Test**: `python3 sst_service.py`
- **TTS Test**: `python3 tts_service.py`
- **Full Pipeline Test**: `python3 test_pipeline.py`

## 🎨 Customization

### Changing the AI Personality

Edit the system prompt in `conversation_pipeline.py`:

```python
system_prompt = """You are a helpful AI assistant. Respond naturally and conversationally. 
Keep your responses concise but informative. Be friendly and engaging."""
```

### Adjusting Response Length

Modify `LLM_MAX_TOKENS` in `config.py`:

```python
LLM_MAX_TOKENS = 150  # Increase for longer responses
```

### Changing Voice

Update TTS settings in `config.py`:

```python
TTS_VOICE = "Mason-PlayAI"  # Change to different voice
```

## 📊 Performance Tips

- **Clear speech**: Speak clearly and at a moderate pace
- **Quiet environment**: Minimize background noise
- **Good microphone**: Use a quality microphone for better accuracy
- **Stable internet**: Ensure reliable internet connection for API calls

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License. 