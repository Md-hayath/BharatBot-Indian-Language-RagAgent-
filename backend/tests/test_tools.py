from tools.language_detector import detect_language

def test_kannada():
    assert detect_language("ನಮಸ್ಕಾರ")["code"] == "kn"
    
def test_hindi():
    assert detect_language("नमस्ते")["code"] == "hi"

def test_english():
    assert detect_language("Hello world")["code"] == "en"

def test_tamil():
    assert detect_language("வணக்கம்")["code"] == "ta"

