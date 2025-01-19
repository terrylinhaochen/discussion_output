# PDF to Podcast

## Overview

This project provides a tool to convert any PDF document into a podcast episode! Using Google's Gemini for dialogue generation and OpenAI's text-to-speech models, this tool processes the content of a PDF, generates a natural dialogue suitable for an audio podcast, and outputs it as an MP3 file.

## Features

- **Convert PDF to Podcast:** Upload a PDF and convert its content into a podcast dialogue.
- **AI-Powered Dialogue:** Uses Google's Gemini LLM to create engaging, natural conversations.
- **High-Quality Audio:** Leverages OpenAI's text-to-speech for lifelike voices.
- **User-friendly Interface:** Simple interface using Gradio for easy interaction.

## Installation

To set up the project, follow these steps:

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