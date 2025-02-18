import os
from dotenv import load_dotenv

load_dotenv()

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

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD2udCMKiixztGCp0gcpB2FDSlKE9s2ypE")
MASTODON_ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN", "bxzgUanrZ3qgXwdNJn9om4XWkcUgMRdmP3K1gUZGXig")
MASTODON_INSTANCE = os.getenv("MASTODON_INSTANCE", "https://mastodon.rd.ai") 