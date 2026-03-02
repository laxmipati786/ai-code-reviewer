"""
Clean Code Scorer Service
Calculates a clean code quality score (0–100) based on multiple weighted factors.
"""
import ast
import re
import math
from typing import Dict


def calculate_clean_code_score(code: str, language: str) -> Dict:
    """
    Calculate clean code score with breakdown.
    Returns dict with overall score and individual metrics.
    """
    lines = code.split('\n')
    non_empty_lines = [l for l in lines if l.strip()]
    loc = len(non_empty_lines)

    if loc == 0:
        return {
            "score": 0,
            "breakdown": {},
            "function_count": 0,
            "loc": 0,
            "comment_ratio": 0
        }

    # Calculate individual scores
    function_length_score = _score_function_length(code, language)
    naming_score = _score_variable_naming(code, language)
    comment_ratio, comment_score = _score_comments(code, language)
    magic_number_score = _score_magic_numbers(code)
    duplication_score = _score_duplication(code)
    indentation_score = _score_indentation(code)
    line_length_score = _score_line_length(code)
    function_count = _count_functions(code, language)

    # Weighted scoring
    weights = {
        "function_length": 0.20,
        "naming_quality": 0.20,
        "comment_ratio": 0.10,
        "magic_numbers": 0.10,
        "duplication": 0.15,
        "indentation": 0.10,
        "line_length": 0.15,
    }

    scores = {
        "function_length": function_length_score,
        "naming_quality": naming_score,
        "comment_ratio": comment_score,
        "magic_numbers": magic_number_score,
        "duplication": duplication_score,
        "indentation": indentation_score,
        "line_length": line_length_score,
    }

    overall = sum(scores[k] * weights[k] for k in weights)

    return {
        "score": round(overall, 1),
        "breakdown": {k: round(v, 1) for k, v in scores.items()},
        "function_count": function_count,
        "loc": loc,
        "comment_ratio": round(comment_ratio, 2)
    }


def _score_function_length(code: str, language: str) -> float:
    """Score based on average function length. Shorter functions = better."""
    if language == "python":
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            if not functions:
                return 80.0

            avg_length = sum(
                node.end_lineno - node.lineno + 1
                for node in functions
                if hasattr(node, 'end_lineno') and node.end_lineno
            ) / len(functions)

            if avg_length <= 10:
                return 100
            elif avg_length <= 20:
                return 90
            elif avg_length <= 30:
                return 75
            elif avg_length <= 50:
                return 55
            else:
                return max(20, 100 - avg_length)
        except SyntaxError:
            pass

    # Generic: count lines between function definitions
    func_patterns = {
        'javascript': r'function\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\(',
        'java': r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\(',
        'cpp': r'[\w:]+\s+\w+\s*\([^)]*\)\s*\{',
        'python': r'def\s+\w+'
    }

    pattern = func_patterns.get(language, func_patterns['python'])
    matches = list(re.finditer(pattern, code))

    if not matches:
        return 80.0

    lines = code.split('\n')
    total_lines = len(lines)
    avg_length = total_lines / len(matches)

    if avg_length <= 15:
        return 100
    elif avg_length <= 25:
        return 85
    elif avg_length <= 40:
        return 65
    else:
        return max(20, 100 - avg_length)


def _score_variable_naming(code: str, language: str) -> float:
    """Score variable naming quality."""
    # Extract identifiers
    identifiers = re.findall(r'\b([a-zA-Z_]\w*)\b', code)

    # Filter out keywords and common names
    keywords = {
        'if', 'else', 'for', 'while', 'return', 'def', 'class', 'import', 'from',
        'in', 'not', 'and', 'or', 'is', 'True', 'False', 'None', 'try', 'except',
        'finally', 'with', 'as', 'pass', 'break', 'continue', 'yield', 'lambda',
        'function', 'var', 'let', 'const', 'new', 'this', 'public', 'private',
        'protected', 'static', 'void', 'int', 'float', 'double', 'string', 'bool',
        'char', 'long', 'short', 'unsigned', 'include', 'using', 'namespace', 'std',
        'cout', 'cin', 'endl', 'printf', 'scanf', 'main', 'null', 'undefined',
        'console', 'log', 'print', 'range', 'len', 'append', 'self', 'super'
    }

    names = [n for n in identifiers if n not in keywords and len(n) > 0]
    if not names:
        return 80.0

    good_names = 0
    total = len(names)

    for name in names:
        # Good: longer than 2 chars OR is common single-letter loop var
        if len(name) > 2 or name in ('i', 'j', 'k', 'x', 'y', 'n'):
            good_names += 1
        # Bad: single character non-standard
        elif len(name) == 1:
            pass  # bad

    # Check naming consistency (snake_case vs camelCase)
    snake_count = sum(1 for n in names if '_' in n)
    camel_count = sum(1 for n in names if re.match(r'^[a-z]+[A-Z]', n))

    consistency_penalty = 0
    if snake_count > 0 and camel_count > 0:
        consistency_penalty = 10  # Mixed naming styles

    score = (good_names / total) * 100 - consistency_penalty
    return max(0, min(100, score))


def _score_comments(code: str, language: str) -> tuple:
    """Score comment ratio. Returns (ratio, score)."""
    lines = code.split('\n')
    total = len([l for l in lines if l.strip()])

    if total == 0:
        return 0, 50

    comment_chars = {'python': '#', 'javascript': '//', 'java': '//', 'cpp': '//'}
    char = comment_chars.get(language, '#')

    comment_lines = sum(1 for l in lines if l.strip().startswith(char))
    # Also count docstrings for Python
    if language == "python":
        in_docstring = False
        for line in lines:
            stripped = line.strip()
            if '"""' in stripped or "'''" in stripped:
                if in_docstring:
                    comment_lines += 1
                    in_docstring = False
                else:
                    comment_lines += 1
                    in_docstring = True
            elif in_docstring:
                comment_lines += 1

    ratio = comment_lines / total

    # Ideal ratio is 10-25%
    if 0.10 <= ratio <= 0.25:
        score = 100
    elif 0.05 <= ratio < 0.10:
        score = 75
    elif 0.25 < ratio <= 0.40:
        score = 80
    elif ratio < 0.05:
        score = 40
    else:
        score = 60  # Over-commented

    return ratio, score


def _score_magic_numbers(code: str) -> float:
    """Score based on magic number usage. Fewer magic numbers = better."""
    # Find numeric literals (excluding 0, 1, 2 which are commonly acceptable)
    numbers = re.findall(r'(?<!=\s)(?<!\w)\b(\d+\.?\d*)\b', code)
    acceptable = {'0', '1', '2', '0.0', '1.0', '100'}
    magic_numbers = [n for n in numbers if n not in acceptable]

    lines = code.split('\n')
    total_lines = len([l for l in lines if l.strip()])

    if total_lines == 0:
        return 100

    ratio = len(magic_numbers) / total_lines

    if ratio <= 0.05:
        return 100
    elif ratio <= 0.10:
        return 85
    elif ratio <= 0.20:
        return 65
    else:
        return max(30, 100 - ratio * 200)


def _score_duplication(code: str) -> float:
    """Score based on code duplication detection."""
    lines = [l.strip() for l in code.split('\n') if l.strip() and not l.strip().startswith(('#', '//'))]

    if len(lines) < 3:
        return 100

    # Check for duplicate sequences of 3+ lines
    duplicates = 0
    seen = set()
    for i in range(len(lines) - 2):
        block = tuple(lines[i:i+3])
        if block in seen:
            duplicates += 1
        seen.add(block)

    if duplicates == 0:
        return 100
    elif duplicates <= 2:
        return 80
    elif duplicates <= 5:
        return 55
    else:
        return max(20, 100 - duplicates * 10)


def _score_indentation(code: str) -> float:
    """Score indentation consistency."""
    lines = code.split('\n')
    indents = []

    for line in lines:
        if line.strip():
            leading = len(line) - len(line.lstrip())
            if leading > 0:
                indents.append(leading)

    if not indents:
        return 100

    # Check if indentation is consistent (all multiples of same number)
    min_indent = min(indents) if indents else 4
    if min_indent == 0:
        min_indent = 4

    inconsistent = sum(1 for i in indents if i % min_indent != 0)
    ratio = inconsistent / len(indents) if indents else 0

    return max(50, 100 - ratio * 100)


def _score_line_length(code: str) -> float:
    """Score based on line length. Lines > 80 chars get penalized."""
    lines = code.split('\n')
    if not lines:
        return 100

    long_lines = sum(1 for l in lines if len(l) > 80)
    very_long = sum(1 for l in lines if len(l) > 120)

    ratio = (long_lines + very_long * 2) / len(lines)

    return max(30, 100 - ratio * 150)


def _count_functions(code: str, language: str) -> int:
    """Count number of functions/methods."""
    patterns = {
        'python': r'\bdef\s+\w+',
        'javascript': r'\bfunction\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\(',
        'java': r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\(',
        'cpp': r'[\w:]+\s+\w+\s*\([^)]*\)\s*\{'
    }

    pattern = patterns.get(language, patterns['python'])
    return len(re.findall(pattern, code))
