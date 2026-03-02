"""
Metrics Calculator Service
Computes maintainability index, readability score, and performance risk alerts.
"""
import ast
import re
import math
from typing import List, Tuple
from app.models.schemas import PerformanceAlert


def calculate_maintainability_index(code: str, language: str, cyclomatic: int) -> float:
    lines = code.split('\n')
    loc = len([l for l in lines if l.strip()])
    if loc == 0:
        return 100.0

    # Halstead volume approximation
    operators = set()
    operands = set()
    total_operators = 0
    total_operands = 0

    op_patterns = r'[+\-*/=%<>!&|^~]|==|!=|<=|>=|and|or|not|in|is'
    id_pattern = r'\b[a-zA-Z_]\w*\b'

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(('#', '//')):
            continue
        ops = re.findall(op_patterns, stripped)
        ids = re.findall(id_pattern, stripped)
        for op in ops:
            operators.add(op)
            total_operators += 1
        for ident in ids:
            operands.add(ident)
            total_operands += 1

    n1 = len(operators) or 1
    n2 = len(operands) or 1
    N1 = total_operators or 1
    N2 = total_operands or 1
    N = N1 + N2
    n = n1 + n2
    volume = N * math.log2(n) if n > 0 else 0

    # MI = 171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(LOC)
    mi = 171 - 5.2 * math.log(max(volume, 1)) - 0.23 * cyclomatic - 16.2 * math.log(max(loc, 1))
    mi = max(0, min(100, mi))
    return round(mi, 1)


def calculate_readability_score(code: str, language: str) -> float:
    lines = code.split('\n')
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        return 100.0

    score = 100.0

    # Average line length penalty
    avg_len = sum(len(l) for l in non_empty) / len(non_empty)
    if avg_len > 80:
        score -= min(20, (avg_len - 80) * 0.5)

    # Very long lines
    long_lines = sum(1 for l in non_empty if len(l) > 100)
    score -= min(15, long_lines * 2)

    # Naming quality
    identifiers = re.findall(r'\b([a-zA-Z_]\w*)\b', code)
    short_names = sum(1 for n in identifiers if len(n) == 1 and n not in 'ijkxyn')
    if identifiers:
        score -= min(15, (short_names / len(identifiers)) * 50)

    # Blank line ratio (readability aid)
    blank_lines = sum(1 for l in lines if not l.strip())
    blank_ratio = blank_lines / len(lines) if lines else 0
    if blank_ratio < 0.05:
        score -= 10  # Too dense
    elif blank_ratio > 0.4:
        score -= 5   # Too sparse

    # Comment presence
    comment_chars = {'python': '#', 'javascript': '//', 'java': '//', 'cpp': '//'}
    cc = comment_chars.get(language, '#')
    comment_lines = sum(1 for l in non_empty if l.strip().startswith(cc))
    comment_ratio = comment_lines / len(non_empty) if non_empty else 0
    if comment_ratio < 0.05:
        score -= 10
    elif comment_ratio > 0.3:
        score -= 5

    return round(max(0, min(100, score)), 1)


def detect_performance_risks(code: str, language: str) -> List[PerformanceAlert]:
    alerts = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # String concatenation in loops
        if re.search(r'for\s|while\s', stripped):
            next_lines = lines[i:i+5] if i < len(lines) else []
            for nl in next_lines:
                if '+=' in nl and ("'" in nl or '"' in nl or 'str' in nl):
                    alerts.append(PerformanceAlert(
                        line=i, message="String concatenation in loop. Use list + join() for better performance.",
                        risk_level="medium", category="string_concat"
                    ))
                    break

        # Nested list comprehension
        if re.search(r'\[.*\bfor\b.*\bfor\b.*\]', stripped):
            alerts.append(PerformanceAlert(
                line=i, message="Nested list comprehension detected — O(n²) memory allocation risk.",
                risk_level="high", category="nested_comprehension"
            ))

        # Repeated function calls that could be cached
        if language == "python" and re.search(r'len\(.*\)', stripped):
            if re.search(r'(for|while)\s', stripped) and 'range(len(' in stripped:
                alerts.append(PerformanceAlert(
                    line=i, message="Consider using enumerate() instead of range(len(...)).",
                    risk_level="low", category="pythonic"
                ))

        # Large data structure creation
        if re.search(r'\[\s*0\s*\]\s*\*\s*\d{4,}', stripped):
            alerts.append(PerformanceAlert(
                line=i, message="Large array allocation detected. Consider using generators or numpy.",
                risk_level="medium", category="memory"
            ))

        # Recursion without memoization
        if language == "python":
            if 'def ' in stripped:
                func_match = re.search(r'def\s+(\w+)', stripped)
                if func_match:
                    func_name = func_match.group(1)
                    func_body = '\n'.join(lines[i:i+20])
                    if func_name in func_body and '@lru_cache' not in '\n'.join(lines[max(0,i-3):i]):
                        if re.search(rf'\b{func_name}\s*\(', func_body):
                            alerts.append(PerformanceAlert(
                                line=i, message=f"Recursive function '{func_name}' without memoization. Consider @lru_cache.",
                                risk_level="high", category="recursion"
                            ))

        # Global variable access in loops
        if re.search(r'\bglobal\b', stripped):
            alerts.append(PerformanceAlert(
                line=i, message="Global variable access is slower than local. Cache in local variable.",
                risk_level="low", category="global_access"
            ))

    return alerts
