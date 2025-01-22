# PDF to Podcast with Mastodon Integration

## Overview

This project converts PDF documents into engaging podcast episodes with multiple speakers! It uses:
- Google's Gemini for natural dialogue generation
- OpenAI's text-to-speech models for voice synthesis
- Mastodon integration for automatic thread posting
- Gradio for the web interface

## Features

- **Smart PDF Processing:** Extracts and analyzes PDF content intelligently
- **Dynamic Dialogue Generation:** Creates natural conversations between multiple speakers
- **Voice Diversity:** Uses multiple distinct voices:
  - Host (Female) - Nova voice
  - Main Speaker - Onyx voice
  - Guest 1 - Alloy voice
  - Guest 2 - Echo voice
  - Guest 3 - Fable voice
  - Guest 4 - Sage voice
- **Mastodon Integration:** Automatically posts podcast content as threaded discussions
- **User-friendly Interface:** Simple Gradio web interface

## Implementation Logic

### 1. PDF Processing
- Extracts text from PDF using PyPDF
- Processes content for dialogue generation

### 2. Dialogue Generation
- Uses Gemini AI to:
  - Analyze content
  - Generate natural dialogue
  - Distribute content among speakers
- Structures conversation with:
  - Introduction
  - Main discussion
  - Supporting viewpoints
  - Conclusion

### 3. Audio Generation
- Converts dialogue to speech using OpenAI's TTS
- Assigns different voices to each speaker
- Concatenates audio segments

### 4. Mastodon Integration
- Posts initial thread with podcast title
- Creates threaded replies for each dialogue segment
- Adds speaker emojis and formatting
- Handles character limits automatically

## Project Structure

pdf-to-podcast/
├── main.py # Main application code
├── requirements.txt # Python dependencies
├── pyproject.toml # Project configuration
├── README.md # Documentation
├── description.md # Gradio interface description
├── .env # Environment variables
├── examples/ # Example PDF files
│ └── .pdf # PDF examples
├── static/ # Static assets
│ └── .png # Static images
└── gradio_cached_examples/ # Cached examples
└── tmp/ # Temporary audio files
└── .mp3 # Generated audio files

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/terrylinhaochen/discussion_output.git
   cd pdf-to-podcast
   ```

2. **Create necessary directories:**
   ```bash
   mkdir -p examples
   mkdir -p static
   mkdir -p gradio_cached_examples/tmp
   ```

3. **Set up environment:**
   ```bash
   # Create .env file with your API keys
   echo "OPENAI_API_KEY=your_key_here" > .env
   echo "MASTODON_ACCESS_TOKEN=your_token_here" >> .env
   echo "MASTODON_INSTANCE=https://mastodon.rd.ai" >> .env
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application:**
   ```bash
   python main.py
   ```

2. **Access the interface:**
   - Open your browser to `http://localhost:7860`
   - Upload a PDF file
   - Optionally provide your OpenAI API key if not in environment
   - Click generate

3. **View Results:**
   - Listen to generated audio
   - View the transcript
   - Check Mastodon thread links

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for text-to-speech
- `MASTODON_ACCESS_TOKEN`: Your Mastodon access token
- `MASTODON_INSTANCE`: Your Mastodon instance URL (default: https://mastodon.rd.ai)

## Dependencies

Key dependencies include:
- `promptic`: For Gemini AI integration
- `openai`: For text-to-speech
- `gradio`: For web interface
- `pypdf`: For PDF processing
- `requests`: For Mastodon API integration

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

Based on the original PDF-to-Podcast converter, enhanced with Mastodon integration and improved dialogue generation.