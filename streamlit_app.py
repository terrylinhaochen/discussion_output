import streamlit as st
import tempfile
from pathlib import Path
from app.config import DEFAULT_PROMPT, OPENAI_API_KEY, GEMINI_API_KEY
from app.audio import process_pdf_to_audio
from app.mastodon import post_to_mastodon

st.set_page_config(
    page_title="Output Generation Demo",
    page_icon="🎙️",
    layout="wide"
)

st.title("Output Generation Demo")
st.markdown("[Demo v0.1] Convert PDF into a podcast episode with multiple persona.")

# File uploader
pdf_file = st.file_uploader("Upload PDF", type="pdf")

# System prompt input
system_prompt = st.text_area(
    "System Prompt",
    value=DEFAULT_PROMPT,
    height=300,
    help="Edit this prompt to customize how the dialogue is generated"
)

# OpenAI API key input (if not set in environment)
openai_api_key = OPENAI_API_KEY
if not openai_api_key:
    openai_api_key = st.text_input("OpenAI API Key", type="password")

if pdf_file and openai_api_key:
    if st.button("Generate Podcast"):
        with st.spinner("Processing..."):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(pdf_file.getvalue())
                pdf_path = Path(tmp_file.name)

            try:
                # Generate audio and transcript
                audio_bytes, transcript = process_pdf_to_audio(
                    pdf_path,
                    system_prompt,
                    openai_api_key,
                    GEMINI_API_KEY
                )

                # Display results
                st.audio(audio_bytes, format="audio/mp3")
                st.text_area("Transcript", transcript, height=400)

                # Post to Mastodon
                try:
                    mastodon_urls = post_to_mastodon(transcript, pdf_file.name)
                    st.json(mastodon_urls)
                except Exception as e:
                    st.error(f"Failed to post to Mastodon: {str(e)}")

            except Exception as e:
                st.error(f"Error generating podcast: {str(e)}")
            finally:
                # Clean up temporary file
                pdf_path.unlink() 