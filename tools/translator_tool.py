from langchain.tools import tool
from sarvamai import SarvamAI
from config.settings import SARVAM_API_KEY

_client = None

def get_client():
    global _client
    if _client is None:
        _client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
    return _client


@tool
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text between languages using Sarvam Mayura API."""
    try:
        response = get_client().text.translate(
            input=text,
            source_language_code=source_lang,
            target_language_code=target_lang,
            model="mayura:v1"
        )
        return response.translated_text
    except Exception as e:
        return f"Translation failed: {e}"