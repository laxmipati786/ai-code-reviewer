"""
Refactoring Engine Service
Detects code patterns that could benefit from refactoring and provides suggestions.
"""
import ast
import re
from typing import List
from app.models.schemas import RefactoringSuggestion


def detect_refactoring_opportunities(code: str, language: str) -> List[RefactoringSuggestion]:
    """Main entry point for refactoring analysis."""
    suggestions = []

    if language == "python":
        suggestions.extend(_analyze_python_refactoring(code))

    suggestions.extend(_analyze_generic_refactoring(code, language))

    return suggestions


def _analyze_python_refactoring(code: str) -> List[RefactoringSuggestion]:
    suggestions = []

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return suggestions

    for node in ast.walk(tree):
        # Long functions
        if isinstance(node, ast.FunctionDef):
            if hasattr(node, 'end_lineno') and node.end_lineno:
                func_length = node.end_lineno - node.lineno + 1
                if func_length > 30:
                    suggestions.append(RefactoringSuggestion(
                        line=node.lineno,
                        message=f"Function '{node.name}' is {func_length} lines long. Consider breaking it into smaller functions.",
                        category="extract_method",
                        priority="high",
                        suggestion=f"Extract logical sections of '{node.name}' into separate helper functions."
                    ))

            # Too many parameters
            param_count = len(node.args.args)
            if param_count > 5:
                suggestions.append(RefactoringSuggestion(
                    line=node.lineno,
                    message=f"Function '{node.name}' has {param_count} parameters. Consider using a data class or dict.",
                    category="reduce_parameters",
                    priority="medium",
                    suggestion="Group related parameters into a class or use **kwargs for optional parameters."
                ))

            # No docstring
            if not (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                suggestions.append(RefactoringSuggestion(
                    line=node.lineno,
                    message=f"Function '{node.name}' lacks a docstring.",
                    category="documentation",
                    priority="low",
                    suggestion=f"Add a docstring describing what '{node.name}' does, its parameters, and return value."
                ))

        # Deep nesting (if/for/while within if/for/while)
        if isinstance(node, (ast.If, ast.For, ast.While)):
            depth = _get_nesting_depth(node)
            if depth >= 3:
                suggestions.append(RefactoringSuggestion(
                    line=node.lineno,
                    message=f"Deeply nested block (depth: {depth}). Consider using early returns or guard clauses.",
                    category="reduce_nesting",
                    priority="high",
                    suggestion="Use early returns, extract nested logic into functions, or use guard clauses to flatten nesting."
                ))

        # Redundant else after return
        if isinstance(node, ast.If) and node.orelse:
            if node.body and isinstance(node.body[-1], ast.Return):
                suggestions.append(RefactoringSuggestion(
                    line=node.lineno,
                    message="Redundant 'else' after 'return'. Remove the else block and un-indent the code.",
                    category="simplify_condition",
                    priority="low",
                    suggestion="Remove the 'else' clause and place its contents at the same indentation level as the 'if'."
                ))

    return suggestions


def _get_nesting_depth(node: ast.AST, depth: int = 0) -> int:
    """Calculate the maximum nesting depth of an AST node."""
    max_depth = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.For, ast.While)):
            child_depth = _get_nesting_depth(child, depth + 1)
            max_depth = max(max_depth, child_depth)
    return max_depth


def _analyze_generic_refactoring(code: str, language: str) -> List[RefactoringSuggestion]:
    suggestions = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detect long lines
        if len(line) > 120:
            suggestions.append(RefactoringSuggestion(
                line=i,
                message=f"Line is {len(line)} characters long. Consider breaking it up.",
                category="line_length",
                priority="low"
            ))

        # Detect hardcoded strings that could be constants
        string_literals = re.findall(r'["\']([^"\']{20,})["\']', stripped)
        for literal in string_literals:
            if not stripped.startswith(('#', '//', 'print', 'console', 'System.out')):
                suggestions.append(RefactoringSuggestion(
                    line=i,
                    message=f"Long string literal detected. Consider extracting to a named constant.",
                    category="extract_constant",
                    priority="low",
                    suggestion=f"Create a constant like: MY_CONSTANT = \"{literal[:30]}...\""
                ))
                break  # Only one suggestion per line

        # Detect commented-out code (heuristic)
        comment_chars = {'python': '#', 'javascript': '//', 'java': '//', 'cpp': '//'}
        cc = comment_chars.get(language, '#')
        if stripped.startswith(cc):
            rest = stripped[len(cc):].strip()
            # Check if it looks like code
            code_indicators = ['=', '(', ')', '{', '}', ';', 'return', 'if ', 'for ', 'while ']
            if any(ind in rest for ind in code_indicators) and len(rest) > 10:
                suggestions.append(RefactoringSuggestion(
                    line=i,
                    message="Commented-out code detected. Remove dead code or use version control.",
                    category="dead_code",
                    priority="medium"
                ))

    # Detect duplicate code blocks
    _detect_duplicates(code, suggestions)

    return suggestions


def _detect_duplicates(code: str, suggestions: List[RefactoringSuggestion]):
    """Detect duplicate code blocks."""
    lines = [l.strip() for l in code.split('\n') if l.strip()]

    if len(lines) < 6:
        return

    # Check for 3-line duplicate blocks
    seen_blocks = {}
    for i in range(len(lines) - 2):
        block = '\n'.join(lines[i:i+3])
        if block in seen_blocks and block.count('\n') >= 2:
            suggestions.append(RefactoringSuggestion(
                line=i + 1,
                message=f"Duplicate code block found (also at line {seen_blocks[block]}). Extract into a reusable function.",
                category="duplication",
                priority="high",
                suggestion="Extract the duplicated logic into a shared function."
            ))
            break  # Only report once
        seen_blocks[block] = i + 1
