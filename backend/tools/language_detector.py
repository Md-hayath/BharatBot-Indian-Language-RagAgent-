from lingua import LanguageDetectorBuilder, IsoCode639_1
from config.languages import get_display

_detector = None

# Kannada and Malayalam aren't in lingua's supported language set at all, so
# they're detected by their (script-unique, so unambiguous) Unicode block
# ranges before falling back to lingua for everything else.
_SCRIPT_RANGES = {
    "kn": (0x0C80, 0x0CFF),  # Kannada
    "ml": (0x0D00, 0x0D7F),  # Malayalam
}

# Restrict lingua to languages BharatBot actually supports (plus Urdu, which
# lingua does support). Building from all 75+ languages it knows made short or
# ambiguous text - e.g. "What is BharatBot?" - misclassify against unrelated
# Latin-script languages like Tagalog.
_SUPPORTED_ISO_CODES = ["EN", "HI", "TA", "TE", "BN", "MR", "GU", "PA", "UR"]


def get_detector():
    global _detector
    if _detector is None:
        codes = [getattr(IsoCode639_1, code) for code in _SUPPORTED_ISO_CODES]
        _detector = LanguageDetectorBuilder.from_iso_codes_639_1(*codes).build()
    return _detector


def _detect_by_script(text: str) -> str | None:
    for code, (lo, hi) in _SCRIPT_RANGES.items():
        if any(lo <= ord(ch) <= hi for ch in text):
            return code
    return None


def detect_language(text: str) -> dict:
    script_code = _detect_by_script(text)
    if script_code:
        return {"code": script_code, "display": get_display(script_code)}

    result = get_detector().detect_language_of(text)
    if result is None:
        return {"code": "en", "display": "🇬🇧 English"}
    code = result.iso_code_639_1.name.lower()
    return {"code": code, "display": get_display(code)}
