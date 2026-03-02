"""
Syntax Analyzer Service
Performs AST-based syntax validation for Python, and regex-based checks for other languages.
"""
import ast
import re
from typing import List, Tuple
from app.models.schemas import SyntaxError_, LogicalWarning


def analyze_syntax(code: str, language: str) -> Tuple[List[SyntaxError_], List[LogicalWarning]]:
    """Main entry point for syntax analysis."""
    if language == "python":
        return _analyze_python(code)
    elif language == "javascript":
        return _analyze_javascript(code)
    elif language == "java":
        return _analyze_java(code)
    elif language == "cpp":
        return _analyze_cpp(code)
    return [], []


def _analyze_python(code: str) -> Tuple[List[SyntaxError_], List[LogicalWarning]]:
    errors = []
    warnings = []

    # AST-based syntax check
    try:
        tree = ast.parse(code)
        # Walk AST for logical warnings
        warnings.extend(_check_python_logic(tree, code))
    except SyntaxError as e:
        errors.append(SyntaxError_(
            line=e.lineno or 1,
            column=e.offset or 0,
            message=str(e.msg),
            severity="error"
        ))

    return errors, warnings


def _check_python_logic(tree: ast.AST, code: str) -> List[LogicalWarning]:
    warnings = []
    lines = code.split('\n')

    for node in ast.walk(tree):
        # Detect bare except
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            warnings.append(LogicalWarning(
                line=node.lineno,
                message="Bare 'except' clause detected. Specify exception type for better error handling.",
                severity="warning",
                category="exception_handling"
            ))

        # Detect mutable default arguments
        if isinstance(node, ast.FunctionDef):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    warnings.append(LogicalWarning(
                        line=node.lineno,
                        message=f"Mutable default argument in function '{node.name}'. Use None and initialize inside the function.",
                        severity="warning",
                        category="mutable_default"
                    ))

        # Detect comparison to None using == instead of 'is'
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(comparator, ast.Constant) and comparator.value is None:
                    warnings.append(LogicalWarning(
                        line=node.lineno,
                        message="Use 'is None' or 'is not None' instead of '==' or '!=' for None comparisons.",
                        severity="info",
                        category="style"
                    ))

        # Detect unused imports (basic)
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                if name.split('.')[0] not in code.replace(f"import {alias.name}", ""):
                    pass  # Could be a false positive, skip for now

        # Detect while True without break
        if isinstance(node, ast.While):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                if not has_break:
                    warnings.append(LogicalWarning(
                        line=node.lineno,
                        message="Infinite loop detected: 'while True' without a 'break' statement.",
                        severity="error",
                        category="infinite_loop"
                    ))

        # Detect variable shadowing built-ins
        builtin_names = {'list', 'dict', 'set', 'str', 'int', 'float', 'type', 'id', 'input', 'print', 'len', 'range', 'map', 'filter'}
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in builtin_names:
                    warnings.append(LogicalWarning(
                        line=node.lineno,
                        message=f"Variable '{target.id}' shadows a Python built-in. Consider using a different name.",
                        severity="warning",
                        category="shadowing"
                    ))

    # Check for TODO/FIXME/HACK comments
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('#'):
            for marker in ['TODO', 'FIXME', 'HACK', 'XXX']:
                if marker in stripped.upper():
                    warnings.append(LogicalWarning(
                        line=i,
                        message=f"'{marker}' comment found: {stripped[:80]}",
                        severity="info",
                        category="comment_marker"
                    ))

    return warnings


def _analyze_javascript(code: str) -> Tuple[List[SyntaxError_], List[LogicalWarning]]:
    errors = []
    warnings = []

    # Check for common syntax issues
    _check_bracket_balance(code, errors)

    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detect var usage (should use let/const)
        if re.match(r'\bvar\s+', stripped):
            warnings.append(LogicalWarning(
                line=i,
                message="Use 'let' or 'const' instead of 'var' for better scoping.",
                severity="warning",
                category="modern_js"
            ))

        # Detect == instead of ===
        if re.search(r'[^=!]==[^=]', stripped) and '===' not in stripped:
            warnings.append(LogicalWarning(
                line=i,
                message="Use '===' instead of '==' for strict equality comparison.",
                severity="warning",
                category="equality"
            ))

        # Detect console.log in production
        if 'console.log' in stripped:
            warnings.append(LogicalWarning(
                line=i,
                message="Remove 'console.log' statements in production code.",
                severity="info",
                category="debugging"
            ))

    return errors, warnings


def _analyze_java(code: str) -> Tuple[List[SyntaxError_], List[LogicalWarning]]:
    errors = []
    warnings = []

    _check_bracket_balance(code, errors)

    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detect System.out.println (debugging)
        if 'System.out.println' in stripped:
            warnings.append(LogicalWarning(
                line=i,
                message="Use a logging framework instead of 'System.out.println'.",
                severity="info",
                category="logging"
            ))

        # Detect catching generic Exception
        if re.search(r'catch\s*\(\s*Exception\s+', stripped):
            warnings.append(LogicalWarning(
                line=i,
                message="Catching generic 'Exception'. Catch specific exception types instead.",
                severity="warning",
                category="exception_handling"
            ))

        # Detect missing semicolons (heuristic)
        if stripped and not stripped.endswith((';', '{', '}', '//', '/*', '*/', '*', '@')) \
           and not stripped.startswith(('import', 'package', '//', '/*', '*', '@', 'public', 'private', 'protected', 'class', 'interface', 'if', 'else', 'for', 'while', 'try', 'catch', 'finally')):
            if not stripped.endswith((')', ',')):
                pass  # Too many false positives for now

    return errors, warnings


def _analyze_cpp(code: str) -> Tuple[List[SyntaxError_], List[LogicalWarning]]:
    errors = []
    warnings = []

    _check_bracket_balance(code, errors)

    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detect raw pointers
        if re.search(r'\b(new|delete)\b', stripped):
            warnings.append(LogicalWarning(
                line=i,
                message="Consider using smart pointers (unique_ptr, shared_ptr) instead of raw new/delete.",
                severity="warning",
                category="memory"
            ))

        # Detect using namespace std
        if 'using namespace std' in stripped:
            warnings.append(LogicalWarning(
                line=i,
                message="Avoid 'using namespace std' in header files. Use explicit std:: prefix.",
                severity="info",
                category="namespace"
            ))

        # Detect printf (prefer cout or fmt)
        if re.search(r'\bprintf\s*\(', stripped):
            warnings.append(LogicalWarning(
                line=i,
                message="Consider using std::cout or std::format for type-safe output.",
                severity="info",
                category="io"
            ))

    return errors, warnings


def _check_bracket_balance(code: str, errors: List[SyntaxError_]):
    """Check for unbalanced brackets."""
    stack = []
    brackets = {'(': ')', '[': ']', '{': '}'}
    closing = set(brackets.values())

    for i, line in enumerate(code.split('\n'), 1):
        in_string = False
        string_char = None
        for j, ch in enumerate(line):
            if ch in ('"', "'") and not in_string:
                in_string = True
                string_char = ch
            elif ch == string_char and in_string:
                in_string = False
            elif not in_string:
                if ch in brackets:
                    stack.append((ch, i, j))
                elif ch in closing:
                    if stack and brackets.get(stack[-1][0]) == ch:
                        stack.pop()
                    else:
                        errors.append(SyntaxError_(
                            line=i,
                            column=j,
                            message=f"Unmatched closing bracket '{ch}'",
                            severity="error"
                        ))

    for bracket, line, col in stack:
        errors.append(SyntaxError_(
            line=line,
            column=col,
            message=f"Unmatched opening bracket '{bracket}'",
            severity="error"
        ))
