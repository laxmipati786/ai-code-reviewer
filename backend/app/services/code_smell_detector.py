"""
Code Smell Detector Service
Identifies common code smells and anti-patterns.
"""
import ast
import re
from typing import List
from app.models.schemas import CodeSmell


def detect_code_smells(code: str, language: str) -> List[CodeSmell]:
    smells = []
    lines = code.split('\n')
    non_empty = [l for l in lines if l.strip()]

    if language == "python":
        smells.extend(_python_smells(code))

    # God function (too long)
    _detect_god_functions(code, language, smells)
    # Excessive parameters
    _detect_excessive_params(code, language, smells)
    # Dead code indicators
    _detect_dead_code(code, language, smells)
    # Feature envy
    _detect_feature_envy(code, language, smells)
    # Long parameter list in calls
    _detect_long_chains(code, smells)

    return smells


def _python_smells(code: str) -> List[CodeSmell]:
    smells = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return smells

    for node in ast.walk(tree):
        # Global variables
        if isinstance(node, ast.Global):
            smells.append(CodeSmell(
                line=node.lineno, message=f"Global variable usage detected. Avoid mutable global state.",
                smell_type="global_state", severity="medium"
            ))
        # Star imports
        if isinstance(node, ast.ImportFrom) and node.names:
            if any(alias.name == '*' for alias in node.names):
                smells.append(CodeSmell(
                    line=node.lineno, message="Wildcard import 'from X import *' pollutes namespace.",
                    smell_type="wildcard_import", severity="medium"
                ))
        # Boolean parameters
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg.startswith('is_') or arg.arg.startswith('has_') or arg.arg == 'flag':
                    smells.append(CodeSmell(
                        line=node.lineno,
                        message=f"Boolean parameter '{arg.arg}' in '{node.name}'. Consider splitting into two functions.",
                        smell_type="boolean_param", severity="low"
                    ))
    return smells


def _detect_god_functions(code: str, language: str, smells: List[CodeSmell]):
    patterns = {'python': r'def\s+(\w+)', 'javascript': r'function\s+(\w+)',
                'java': r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\(',
                'cpp': r'[\w:]+\s+(\w+)\s*\([^)]*\)\s*\{'}
    pattern = patterns.get(language, patterns['python'])
    matches = list(re.finditer(pattern, code))
    lines = code.split('\n')
    for i, match in enumerate(matches):
        start_line = code[:match.start()].count('\n') + 1
        end_line = code[:matches[i+1].start()].count('\n') if i+1 < len(matches) else len(lines)
        length = end_line - start_line
        if length > 50:
            smells.append(CodeSmell(
                line=start_line, message=f"Function '{match.group(1)}' is {length} lines — God function detected.",
                smell_type="god_function", severity="high"
            ))


def _detect_excessive_params(code: str, language: str, smells: List[CodeSmell]):
    if language == "python":
        pattern = r'def\s+(\w+)\s*\(([^)]*)\)'
    else:
        pattern = r'(?:function\s+)?(\w+)\s*\(([^)]*)\)'
    for match in re.finditer(pattern, code):
        params = [p.strip() for p in match.group(2).split(',') if p.strip()]
        params = [p for p in params if p != 'self' and p != 'this']
        if len(params) > 5:
            line = code[:match.start()].count('\n') + 1
            smells.append(CodeSmell(
                line=line, message=f"Function '{match.group(1)}' has {len(params)} params. Use an object/class.",
                smell_type="long_param_list", severity="medium"
            ))


def _detect_dead_code(code: str, language: str, smells: List[CodeSmell]):
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('pass') and len(stripped) == 4:
            smells.append(CodeSmell(
                line=i, message="'pass' statement — possible dead code or incomplete implementation.",
                smell_type="dead_code", severity="low"
            ))
        if stripped == 'return' and i < len(lines):
            next_lines = [l.strip() for l in lines[i:i+3] if l.strip()]
            if next_lines and not next_lines[0].startswith(('def ', 'class ', 'elif ', 'else:', 'except', 'finally')):
                smells.append(CodeSmell(
                    line=i+1, message="Unreachable code after 'return' statement.",
                    smell_type="unreachable_code", severity="high"
                ))


def _detect_feature_envy(code: str, language: str, smells: List[CodeSmell]):
    if language != "python":
        return
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            attr_access = {}
            for child in ast.walk(node):
                if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name):
                    obj = child.value.id
                    if obj != 'self':
                        attr_access[obj] = attr_access.get(obj, 0) + 1
            for obj, count in attr_access.items():
                if count >= 4:
                    smells.append(CodeSmell(
                        line=node.lineno,
                        message=f"Function '{node.name}' accesses '{obj}' {count} times — possible Feature Envy.",
                        smell_type="feature_envy", severity="medium"
                    ))


def _detect_long_chains(code: str, smells: List[CodeSmell]):
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        chain_count = line.count('.')
        if chain_count >= 4:
            smells.append(CodeSmell(
                line=i, message=f"Method chain with {chain_count} calls. Consider breaking into intermediate variables.",
                smell_type="long_chain", severity="low"
            ))
