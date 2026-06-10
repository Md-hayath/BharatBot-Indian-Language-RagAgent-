from tools.language_detector import detect_language
from tools.retriever_tool import search_documents

queries = [
    "What is this document about?",
    "इस दस्तावेज़ में क्या है?",
    "இந்த ஆவணம் என்ன?",
    "ఈ పత్రం దేని గురించి?"
]

for q in queries:
    lang = detect_language(q)
    print(f"\nQuery   : {q}")
    print(f"Language: {lang['display']}")
    result = search_documents(q)
    print(f"Result  : {result[:200]}...")