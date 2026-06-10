LANGUAGE_CONFIG = {
    "hi": {"name": "Hindi",     "native": "हिन्दी",    "flag": "🇮🇳", "tesseract": "hin", "folder": "hindi"},
    "ta": {"name": "Tamil",     "native": "தமிழ்",      "flag": "🇮🇳", "tesseract": "tam", "folder": "tamil"},
    "te": {"name": "Telugu",    "native": "తెలుగు",     "flag": "🇮🇳", "tesseract": "tel", "folder": "telugu"},
    "kn": {"name": "Kannada",   "native": "ಕನ್ನಡ",      "flag": "🇮🇳", "tesseract": "kan", "folder": "english"},
    "ml": {"name": "Malayalam", "native": "മലയാളം",     "flag": "🇮🇳", "tesseract": "mal", "folder": "english"},
    "bn": {"name": "Bengali",   "native": "বাংলা",       "flag": "🇮🇳", "tesseract": "ben", "folder": "english"},
    "mr": {"name": "Marathi",   "native": "मराठी",      "flag": "🇮🇳", "tesseract": "mar", "folder": "hindi"},
    "gu": {"name": "Gujarati",  "native": "ગુજરાતી",    "flag": "🇮🇳", "tesseract": "guj", "folder": "english"},
    "pa": {"name": "Punjabi",   "native": "ਪੰਜਾਬੀ",    "flag": "🇮🇳", "tesseract": "pan", "folder": "english"},
    "en": {"name": "English",   "native": "English",    "flag": "🇬🇧", "tesseract": "eng", "folder": "english"},
}

TESSERACT_ALL = "+".join([v["tesseract"] for v in LANGUAGE_CONFIG.values()])

def get_display(code: str) -> str:
    c = LANGUAGE_CONFIG.get(code, {})
    return f"{c.get('flag','🌐')} {c.get('name', code.upper())}"

def get_folder(code: str) -> str:
    return LANGUAGE_CONFIG.get(code, {}).get("folder", "english")