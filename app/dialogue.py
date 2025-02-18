from typing import List, Literal
from pydantic import BaseModel
from promptic import llm
from tenacity import retry, retry_if_exception_type
from pydantic import ValidationError

class DialogueItem(BaseModel):
    text: str
    speaker: Literal["host-female", "main-speaker", "guest-1", "guest-2", "guest-3", "guest-4"]

    @property
    def voice(self):
        return {
            "host-female": "nova",      # Clear, professional female host voice
            "main-speaker": "onyx",     # Deep, authoritative male host voice
            "guest-1": "alloy",         # Balanced, neutral voice
            "guest-2": "echo",          # Younger-sounding voice
            "guest-3": "fable",         # Warm, welcoming voice
            "guest-4": "sage",          # Mature, knowledgeable-sounding voice
        }[self.speaker]

class Dialogue(BaseModel):
    scratchpad: str
    dialogue: List[DialogueItem]

@retry(retry=retry_if_exception_type(ValidationError))
@llm(model="gemini/gemini-1.5-flash-002")
def generate_dialogue(text: str, prompt: str, api_key: str) -> Dialogue:
    """
    {prompt}

    Here is the input text you will be working with:

    <input_text>
    {text}
    </input_text>
    """ 