"""
Complexity Analyzer Service
Estimates Time and Space complexity using AST analysis and pattern matching.
"""
import ast
import re
from typing import Tuple


def analyze_complexity(code: str, language: str) -> Tuple[str, str, int]:
    """
    Returns (time_complexity, space_complexity, cyclomatic_complexity).
    """
    if language == "python":
        return _analyze_python_complexity(code)
    else:
        return _analyze_generic_complexity(code, language)


def _analyze_python_complexity(code: str) -> Tuple[str, str, int]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return _analyze_generic_complexity(code, "python")

    time_complexity = _estimate_time_complexity_ast(tree)
    space_complexity = _estimate_space_complexity_ast(tree, code)
    cyclomatic = _calculate_cyclomatic_complexity(tree)

    return time_complexity, space_complexity, cyclomatic


def _estimate_time_complexity_ast(tree: ast.AST) -> str:
    """Estimate Big-O time complexity from AST."""
    max_depth = 0
    has_recursion = False
    has_divide_and_conquer = False
    has_sorting = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check for recursion
            func_name = node.name
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name) and child.func.id == func_name:
                        has_recursion = True
                        # Check if it's divide and conquer (halving pattern)
                        for arg in child.args:
                            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.FloorDiv):
                                has_divide_and_conquer = True

    # Count nested loop depth
    max_depth = _get_max_loop_depth(tree)

    # Check for built-in sorting
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'sorted':
                has_sorting = True
            elif isinstance(node.func, ast.Attribute) and node.func.attr == 'sort':
                has_sorting = True

    # Determine complexity
    if has_recursion and has_divide_and_conquer:
        return "O(n log n)"
    elif has_recursion:
        return "O(2^n)"
    elif max_depth >= 3:
        return "O(n³)"
    elif max_depth == 2:
        return "O(n²)"
    elif has_sorting and max_depth <= 1:
        return "O(n log n)"
    elif max_depth == 1:
        return "O(n)"
    else:
        return "O(1)"


def _get_max_loop_depth(node: ast.AST, current_depth: int = 0) -> int:
    """Recursively find the maximum nesting depth of loops."""
    max_depth = current_depth

    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.For, ast.While)):
            child_depth = _get_max_loop_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        else:
            child_depth = _get_max_loop_depth(child, current_depth)
            max_depth = max(max_depth, child_depth)

    return max_depth


def _estimate_space_complexity_ast(tree: ast.AST, code: str) -> str:
    """Estimate space complexity based on data structure allocations."""
    list_creations = 0
    dict_creations = 0
    nested_structures = False

    for node in ast.walk(tree):
        if isinstance(node, ast.List):
            list_creations += 1
            # Check for nested lists
            for child in ast.walk(node):
                if isinstance(child, ast.List) and child is not node:
                    nested_structures = True

        if isinstance(node, ast.Dict):
            dict_creations += 1

        # Check for list comprehensions or generator expressions
        if isinstance(node, ast.ListComp):
            list_creations += 1
            if any(isinstance(gen, ast.comprehension) for gen in node.generators):
                if len(node.generators) > 1:
                    nested_structures = True

        # Check for recursive calls (recursive stack space)
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name) and child.func.id == func_name:
                        return "O(n)"  # Recursive stack

    if nested_structures:
        return "O(n²)"
    elif list_creations + dict_creations > 0:
        return "O(n)"
    else:
        return "O(1)"


def _calculate_cyclomatic_complexity(tree: ast.AST) -> int:
    """Calculate McCabe's cyclomatic complexity."""
    complexity = 1  # Base complexity

    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
        elif isinstance(node, ast.ExceptHandler):
            complexity += 1
        elif isinstance(node, ast.With):
            complexity += 1
        elif isinstance(node, ast.Assert):
            complexity += 1
        elif isinstance(node, ast.comprehension):
            complexity += 1
            if node.ifs:
                complexity += len(node.ifs)

    return complexity


def _analyze_generic_complexity(code: str, language: str) -> Tuple[str, str, int]:
    """Regex-based complexity analysis for non-Python languages."""
    lines = code.split('\n')

    # Count loop nesting
    max_loop_depth = _count_loop_nesting_generic(code, language)

    # Check for recursion patterns
    has_recursion = _detect_recursion_generic(code, language)

    # Check for sorting
    has_sorting = bool(re.search(r'\b(sort|Arrays\.sort|std::sort|\.sort\()\b', code))

    # Time complexity
    if has_recursion:
        if re.search(r'/\s*2|>>\s*1|\.length\s*/\s*2|/2', code):
            time = "O(n log n)"
        else:
            time = "O(2^n)"
    elif max_loop_depth >= 3:
        time = "O(n³)"
    elif max_loop_depth == 2:
        time = "O(n²)"
    elif has_sorting:
        time = "O(n log n)"
    elif max_loop_depth == 1:
        time = "O(n)"
    else:
        time = "O(1)"

    # Space complexity (simplified)
    array_pattern = r'\bnew\s+(int|float|double|char|String)\s*\[|new\s+ArrayList|new\s+HashMap|new\s+vector|\[\s*\]|Array\('
    array_creations = len(re.findall(array_pattern, code))
    space = "O(n)" if array_creations > 0 else "O(1)"

    # Cyclomatic complexity
    cyclomatic = 1
    decision_patterns = [
        r'\bif\b', r'\belse\s+if\b', r'\belif\b', r'\bfor\b',
        r'\bwhile\b', r'\bcase\b', r'\bcatch\b', r'\b\?\s*',
        r'\b&&\b', r'\b\|\|\b'
    ]
    for pattern in decision_patterns:
        cyclomatic += len(re.findall(pattern, code))

    return time, space, cyclomatic


def _count_loop_nesting_generic(code: str, language: str) -> int:
    """Count maximum loop nesting depth for any language."""
    max_depth = 0
    current_depth = 0
    lines = code.split('\n')

    loop_patterns = [r'\bfor\b', r'\bwhile\b', r'\bdo\b']

    brace_depth = 0
    loop_depths = []

    for line in lines:
        stripped = line.strip()
        for pattern in loop_patterns:
            if re.search(pattern, stripped):
                current_depth = sum(1 for d in loop_depths if d <= brace_depth) + 1
                loop_depths.append(brace_depth)
                max_depth = max(max_depth, current_depth)

        brace_depth += stripped.count('{') - stripped.count('}')
        if brace_depth < 0:
            brace_depth = 0

    return max_depth


def _detect_recursion_generic(code: str, language: str) -> bool:
    """Detect recursive function calls."""
    if language == "javascript":
        func_pattern = r'function\s+(\w+)'
    elif language == "java":
        func_pattern = r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\('
    elif language == "cpp":
        func_pattern = r'[\w:]+\s+(\w+)\s*\([^)]*\)\s*\{'
    else:
        func_pattern = r'def\s+(\w+)'

    functions = re.findall(func_pattern, code)
    for func_name in functions:
        # Check if function calls itself
        call_pattern = rf'\b{re.escape(func_name)}\s*\('
        func_match = re.search(rf'{re.escape(func_name)}\s*\(', code)
        if func_match:
            calls = re.findall(call_pattern, code)
            if len(calls) > 1:  # Definition + call
                return True

    return False
