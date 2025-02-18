import io
import concurrent.futures as cf
from openai import OpenAI
from pathlib import Path
from app.dialogue import generate_dialogue, Dialogue

def get_mp3(text: str, voice: str, api_key: str) -> bytes:
    client = OpenAI(api_key=api_key)
    
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=voice,
        input=text,
    ) as response:
        with io.BytesIO() as file:
            for chunk in response.iter_bytes():
                file.write(chunk)
            return file.getvalue()

def process_pdf_to_audio(
    pdf_file: Path,
    prompt: str,
    openai_api_key: str,
    gemini_api_key: str
) -> tuple[bytes, str]:
    # Extract text from PDF
    from pypdf import PdfReader
    text = "\n\n".join([page.extract_text() for page in PdfReader(pdf_file).pages])
    
    # Generate dialogue
    llm_output = generate_dialogue(text, prompt, gemini_api_key)
    
    # Generate audio in parallel
    audio = b""
    transcript = ""
    
    with cf.ThreadPoolExecutor() as executor:
        futures = []
        for line in llm_output.dialogue:
            transcript_line = f"{line.speaker}: {line.text}"
            future = executor.submit(get_mp3, line.text, line.voice, openai_api_key)
            futures.append((future, transcript_line))
            
        for future, transcript_line in futures:
            audio_chunk = future.result()
            audio += audio_chunk
            transcript += transcript_line + "\n\n"
            
    return audio, transcript 