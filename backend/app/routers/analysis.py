"""
Analysis Router — Main API endpoint that orchestrates all analysis services.
"""
import time
from fastapi import APIRouter, HTTPException
from app.models.schemas import CodeSubmission, AnalysisResponse
from app.services.syntax_analyzer import analyze_syntax
from app.services.complexity_analyzer import analyze_complexity
from app.services.clean_code_scorer import calculate_clean_code_score
from app.services.refactoring_engine import detect_refactoring_opportunities
from app.services.security_scanner import scan_security
from app.services.similarity_detector import detect_similarity
from app.services.code_smell_detector import detect_code_smells
from app.services.metrics_calculator import (
    calculate_maintainability_index,
    calculate_readability_score,
    detect_performance_risks,
)

router = APIRouter(prefix="/api", tags=["analysis"])

# In-memory history store
_history = []


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(submission: CodeSubmission):
    """Analyze submitted code and return comprehensive report."""
    start = time.time()
    code = submission.code
    lang = submission.language.value

    if not code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    # 1. Syntax analysis
    syntax_errors, logical_warnings = analyze_syntax(code, lang)

    # 2. Complexity analysis
    time_complexity, space_complexity, cyclomatic = analyze_complexity(code, lang)

    # 3. Clean code score
    score_data = calculate_clean_code_score(code, lang)

    # 4. Refactoring suggestions
    refactoring = detect_refactoring_opportunities(code, lang)

    # 5. Security scan
    security = scan_security(code, lang)

    # 6. Similarity detection
    similarity, _ = detect_similarity(code, lang)

    # 7. Code smells
    smells = detect_code_smells(code, lang)

    # 8. Metrics
    maintainability = calculate_maintainability_index(code, lang, cyclomatic)
    readability = calculate_readability_score(code, lang)
    perf_alerts = detect_performance_risks(code, lang)

    # 9. AI explanation
    explanation = _generate_explanation(code, lang, time_complexity, score_data["score"])

    elapsed = (time.time() - start) * 1000

    response = AnalysisResponse(
        syntax_errors=syntax_errors,
        logical_warnings=logical_warnings,
        time_complexity=time_complexity,
        space_complexity=space_complexity,
        clean_code_score=score_data["score"],
        cyclomatic_complexity=cyclomatic,
        similarity_score=similarity,
        security_issues=security,
        refactoring_suggestions=refactoring,
        code_smells=smells,
        maintainability_index=maintainability,
        readability_score=readability,
        performance_alerts=perf_alerts,
        loc=score_data["loc"],
        comment_ratio=score_data["comment_ratio"],
        function_count=score_data["function_count"],
        ai_explanation=explanation,
        analysis_time_ms=round(elapsed, 2),
        language=lang,
    )

    # Store in history
    _history.append({
        "code": code[:200],
        "language": lang,
        "filename": submission.filename,
        "clean_code_score": score_data["score"],
        "time_complexity": time_complexity,
        "timestamp": time.time(),
    })
    if len(_history) > 100:
        _history.pop(0)

    return response


@router.get("/history")
async def get_history():
    return list(reversed(_history[:50]))


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Code Reviewer"}


def _generate_explanation(code: str, lang: str, complexity: str, score: float) -> str:
    lines = code.strip().split('\n')
    loc = len([l for l in lines if l.strip()])

    parts = [f"This {lang} code has {loc} lines of code."]

    if complexity == "O(1)":
        parts.append("It runs in constant time — very efficient!")
    elif complexity == "O(n)":
        parts.append("It has linear time complexity, scaling proportionally with input size.")
    elif complexity == "O(n²)":
        parts.append("It has quadratic time complexity due to nested iterations. May be slow for large inputs.")
    elif complexity == "O(n³)":
        parts.append("It has cubic time complexity — three levels of nesting. Consider algorithm optimization.")
    elif complexity == "O(n log n)":
        parts.append("It has O(n log n) complexity, typical of efficient sorting algorithms.")
    elif complexity == "O(2^n)":
        parts.append("It has exponential time complexity — recursive without memoization. Consider dynamic programming.")
    elif complexity == "O(log n)":
        parts.append("It has logarithmic time complexity — very efficient, likely using divide-and-conquer.")

    if score >= 80:
        parts.append(f"Code quality is excellent (score: {score}/100).")
    elif score >= 60:
        parts.append(f"Code quality is good but has room for improvement (score: {score}/100).")
    elif score >= 40:
        parts.append(f"Code quality needs attention (score: {score}/100). Review the suggestions below.")
    else:
        parts.append(f"Code quality is poor (score: {score}/100). Significant refactoring recommended.")

    return " ".join(parts)
