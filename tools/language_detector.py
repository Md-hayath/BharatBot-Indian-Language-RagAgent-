from lingua import LanguageDetectorBuilder
from config.languages import get_display

_detector = None

def get_detector():
    global _detector
    if _detector is None:
        _detector = LanguageDetectorBuilder.from_all_languages().build()
    return _detector

def detect_language(text: str) -> dict:
    result = get_detector().detect_language_of(text)
    if result is None:
        return {"code": "en", "display": "🇬🇧 English"}
    code = result.iso_code_639_1.name.lower()
    return {"code": code, "display": get_display(code)}