# focus on complete workflows rather than perfect generation.

import concurrent.futures as cf
import glob
import io
import os
import time
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Literal

import gradio as gr
import sentry_sdk
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger
from openai import OpenAI
from promptic import llm
from pydantic import BaseModel, ValidationError
from pypdf import PdfReader
from tenacity import retry, retry_if_exception_type
import requests


if sentry_dsn := os.getenv("SENTRY_DSN"):
    sentry_sdk.init(sentry_dsn)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


class DialogueItem(BaseModel):
    text: str
    speaker: Literal["host-female", "main-speaker", "guest-1", "guest-2", "guest-3", "guest-4"]

    @property
    def voice(self):
        return {
            "host-female": "nova",      # Clear, professional female host voice
            "main-speaker": "onyx",        # Deep, authoritative male host voice
            "guest-1": "alloy",         # Balanced, neutral voice
            "guest-2": "echo",          # Younger-sounding voice
            "guest-3": "fable",         # Warm, welcoming voice
            "guest-4": "sage",          # Mature, knowledgeable-sounding voice
        }[self.speaker]


class Dialogue(BaseModel):
    scratchpad: str
    dialogue: List[DialogueItem]


def get_mp3(text: str, voice: str, api_key: str = None) -> bytes:
    client = OpenAI(
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
    )

    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=voice,
        input=text,
    ) as response:
        with io.BytesIO() as file:
            for chunk in response.iter_bytes():
                file.write(chunk)
            return file.getvalue()


DEFAULT_PROMPT = '''Your task is to take the input text provided and turn it into an engaging, dramatic podcast dialogue featuring four distinct voices discussing interconnected books and ideas. The input text may be messy or unstructured, as it could come from various sources like PDFs or web pages. Focus on extracting key points and creating compelling conversations that reveal hidden patterns and unexpected connections.

Important Formatting Rules:
1. Do not use any bracketed placeholders or sound effects (e.g., no [Host], [Guest], or (sound effects))
2. Match voice gender to speaker gender - use male voices for male authors and female voices for female authors
3. Write dialogue to be read aloud directly - it will be converted to audio without modification
4. Begin each line with the speaker's actual name
5. Keep dialogue natural and conversational - avoid any formatting or stage directions
6. Each speaker must introduce themselves naturally when they first enter the conversation

Speaker Roles:
- Host: Guides the conversation, draws connections, and asks probing questions
- Main Speaker: Author of the core pattern book, leading the primary discussion
- Guest 1 & 2: Authors of supporting books, offering complementary perspectives'''

def generate_audio(file: str, prompt: str = DEFAULT_PROMPT, openai_api_key: str = None) -> tuple:
    if not (os.getenv("OPENAI_API_KEY") or openai_api_key):
        raise gr.Error("OpenAI API key is required")

    with Path(file).open("rb") as f:
        reader = PdfReader(f)
        text = "\n\n".join([page.extract_text() for page in reader.pages])

    @retry(retry=retry_if_exception_type(ValidationError))
    @llm(
        model="gemini/gemini-1.5-flash-002",
        api_key="AIzaSyD2udCMKiixztGCp0gcpB2FDSlKE9s2ypE"
    )
    def generate_dialogue(text: str, prompt: str) -> Dialogue:
        """
        {prompt}

        Here is the input text you will be working with:

        <input_text>
        {text}
        </input_text>
        """

    llm_output = generate_dialogue(text, prompt)

    audio = b""
    transcript = ""

    characters = 0

    with cf.ThreadPoolExecutor() as executor:
        futures = []
        for line in llm_output.dialogue:
            transcript_line = f"{line.speaker}: {line.text}"
            future = executor.submit(get_mp3, line.text, line.voice, openai_api_key)
            futures.append((future, transcript_line))
            characters += len(line.text)

        for future, transcript_line in futures:
            audio_chunk = future.result()
            audio += audio_chunk
            transcript += transcript_line + "\n\n"

    logger.info(f"Generated {characters} characters of audio")

    temporary_directory = "./gradio_cached_examples/tmp/"
    os.makedirs(temporary_directory, exist_ok=True)

    # we use a temporary file because Gradio's audio component doesn't work with raw bytes in Safari
    temporary_file = NamedTemporaryFile(
        dir=temporary_directory,
        delete=False,
        suffix=".mp3",
    )
    temporary_file.write(audio)
    temporary_file.close()

    # Delete any files in the temp directory that end with .mp3 and are over a day old
    for file in glob.glob(f"{temporary_directory}*.mp3"):
        if os.path.isfile(file) and time.time() - os.path.getmtime(file) > 24 * 60 * 60:
            os.remove(file)

    # Get the PDF title
    pdf_title = Path(file).stem

    # After generating the transcript
    mastodon_urls = None
    try:
        mastodon_urls = post_to_mastodon(transcript, pdf_title)
        logger.info(f"Successfully posted podcast to Mastodon for {pdf_title}")
    except Exception as e:
        logger.error(f"Failed to post to Mastodon: {str(e)}")

    return temporary_file.name, transcript, mastodon_urls


demo = gr.Interface(
    title="Output Generation Demo",
    description=Path("description.md").read_text(),
    fn=generate_audio,
    examples=[[str(p)] for p in Path("examples").glob("*.pdf")],
    inputs=[
        gr.File(label="PDF"),
        gr.Textbox(
            label="System Prompt", 
            value=DEFAULT_PROMPT,
            lines=10,
            info="Edit this prompt to customize how the dialogue is generated"
        ),
        gr.Textbox(label="OpenAI API Key", visible=not os.getenv("OPENAI_API_KEY")),
    ],
    outputs=[
        gr.Audio(label="Audio", format="mp3"),
        gr.Textbox(label="Transcript"),
        gr.JSON(label="Mastodon Posts")
    ],
    allow_flagging="never",
    clear_btn=None,
    head=os.getenv("HEAD", "") + Path("head.html").read_text(),
    cache_examples="lazy",
    api_name=False,
)


demo = demo.queue(
    max_size=20,
    default_concurrency_limit=20,
)

app = gr.mount_gradio_app(app, demo, path="/")

def post_to_mastodon(transcript: str, pdf_title: str) -> dict:
    """Posts the podcast transcript as a thread to Mastodon"""
    mastodon_instance = os.getenv('MASTODON_INSTANCE', 'https://mastodon.rd.ai')
    access_token = os.getenv('MASTODON_ACCESS_TOKEN', 'bxzgUanrZ3qgXwdNJn9om4XWkcUgMRdmP3K1gUZGXig')
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        # Post main content
        main_content = f"🎙️ New AI Podcast Discussion: {pdf_title}\n\n#AIPodcast"
        main_post = requests.post(
            f"{mastodon_instance}/api/v1/statuses",
            json={
                "status": main_content,
                "visibility": "public"
            },
            headers=headers
        ).json()

        # Split and post replies
        chunks = []
        current_chunk = ""
        
        for line in transcript.strip().split('\n\n'):
            if not line.strip():
                continue
                
            speaker, text = line.split(':', 1)
            emoji = {
                'host-female': '👩‍🎤',
                'main-speaker': '🎙️',
                'guest-1': '👤',
                'guest-2': '👥',
                'guest-3': '🗣️',
                'guest-4': '💭'
            }.get(speaker.strip(), '🎯')
            
            formatted_line = f"{emoji} {speaker}: {text.strip()}"
            
            if len(current_chunk + "\n\n" + formatted_line) > 450:
                chunks.append(current_chunk)
                current_chunk = formatted_line
            else:
                current_chunk = current_chunk + "\n\n" + formatted_line if current_chunk else formatted_line

        if current_chunk:
            chunks.append(current_chunk)

        # Post replies
        reply_posts = []
        last_post_id = main_post['id']
        
        for chunk in chunks:
            reply = requests.post(
                f"{mastodon_instance}/api/v1/statuses",
                json={
                    "status": chunk,
                    "in_reply_to_id": last_post_id,
                    "visibility": "public"
                },
                headers=headers
            ).json()
            reply_posts.append(reply)
            last_post_id = reply['id']

        return {
            'mainPost': {
                'url': main_post['url'],
                'id': main_post['id']
            },
            'replyPosts': [
                {
                    'url': post['url'],
                    'id': post['id']
                }
                for post in reply_posts
            ]
        }

    except Exception as e:
        logger.error(f"Failed to post to Mastodon: {str(e)}")
        raise

if __name__ == "__main__":
    demo.launch(show_api=False)
