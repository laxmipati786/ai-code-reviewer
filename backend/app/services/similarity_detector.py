"""
Similarity Detector Service
Uses TF-IDF vectorization and cosine similarity to detect code plagiarism.
"""
import re
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_code_corpus: List[str] = []
_corpus_metadata: List[dict] = []

_baseline_patterns = [
    "def bubble_sort(arr):\n    for i in range(len(arr)):\n        for j in range(len(arr)-i-1):\n            if arr[j]>arr[j+1]: arr[j],arr[j+1]=arr[j+1],arr[j]",
    "def binary_search(arr, t):\n    l,r=0,len(arr)-1\n    while l<=r:\n        m=(l+r)//2\n        if arr[m]==t: return m\n        elif arr[m]<t: l=m+1\n        else: r=m-1\n    return -1",
    "def fibonacci(n):\n    if n<=1: return n\n    return fibonacci(n-1)+fibonacci(n-2)",
]


def _preprocess_code(code: str) -> str:
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'"[^"]*"', '""', code)
    code = re.sub(r"'[^']*'", "''", code)
    code = re.sub(r'\s+', ' ', code).strip().lower()
    return code


def detect_similarity(code: str, language: str = "python") -> Tuple[float, str]:
    processed = _preprocess_code(code)
    if not processed or len(processed) < 10:
        return 0.0, ""

    corpus = [_preprocess_code(p) for p in _baseline_patterns] + \
             [_preprocess_code(c) for c in _code_corpus]

    if not corpus:
        _code_corpus.append(code)
        _corpus_metadata.append({"language": language})
        return 0.0, ""

    all_texts = corpus + [processed]
    try:
        vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4), max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]
        max_sim = float(max(similarities)) * 100
        max_idx = int(similarities.argmax())
        source = "common algorithm pattern" if max_idx < len(_baseline_patterns) else "previous submission"
        _code_corpus.append(code)
        _corpus_metadata.append({"language": language})
        if len(_code_corpus) > 1000:
            _code_corpus.pop(0)
            _corpus_metadata.pop(0)
        return round(max_sim, 1), source
    except Exception:
        _code_corpus.append(code)
        _corpus_metadata.append({"language": language})
        return 0.0, ""


def get_corpus_size() -> int:
    return len(_code_corpus) + len(_baseline_patterns)


def clear_corpus():
    _code_corpus.clear()
    _corpus_metadata.clear()
