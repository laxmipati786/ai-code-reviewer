"""
Security Scanner Service
Detects common security vulnerabilities and anti-patterns in code.
"""
import re
from typing import List
from app.models.schemas import SecurityIssue


# Security patterns by category
SECURITY_PATTERNS = {
    "hardcoded_secrets": {
        "patterns": [
            r'(?i)(password|passwd|pwd|secret|api_key|apikey|token|auth_token|access_key|secret_key)\s*=\s*["\'][^"\']{3,}["\']',
            r'(?i)(password|passwd|pwd|secret|api_key|apikey|token)\s*:\s*["\'][^"\']{3,}["\']',
            r'(?i)Bearer\s+[a-zA-Z0-9\-._~+/]+=*',
            r'(?i)(aws_access_key_id|aws_secret_access_key)\s*=\s*["\'][^"\']+["\']',
        ],
        "message": "Hardcoded credential detected. Use environment variables or a secrets manager.",
        "severity": "critical",
        "cwe": "CWE-798"
    },
    "eval_usage": {
        "patterns": [
            r'\beval\s*\(',
            r'\bexec\s*\(',
            r'\b__import__\s*\(',
        ],
        "message": "Dangerous function usage. 'eval'/'exec' can execute arbitrary code.",
        "severity": "critical",
        "cwe": "CWE-95"
    },
    "sql_injection": {
        "patterns": [
            r'(?i)(execute|cursor\.execute|query)\s*\(\s*["\'].*%s.*["\']',
            r'(?i)(execute|cursor\.execute|query)\s*\(\s*f["\']',
            r'(?i)(execute|cursor\.execute)\s*\([^)]*\+[^)]*\)',
            r'(?i)\"SELECT.*\"\s*\+\s*',
            r'(?i)\"INSERT.*\"\s*\+\s*',
            r'(?i)\"UPDATE.*\"\s*\+\s*',
            r'(?i)\"DELETE.*\"\s*\+\s*',
        ],
        "message": "Potential SQL injection vulnerability. Use parameterized queries.",
        "severity": "critical",
        "cwe": "CWE-89"
    },
    "xss": {
        "patterns": [
            r'innerHTML\s*=',
            r'document\.write\s*\(',
            r'\.html\s*\(\s*[^)]*\+',
            r'dangerouslySetInnerHTML',
        ],
        "message": "Potential Cross-Site Scripting (XSS) vulnerability. Sanitize user input before rendering.",
        "severity": "high",
        "cwe": "CWE-79"
    },
    "path_traversal": {
        "patterns": [
            r'open\s*\([^)]*\+[^)]*\)',
            r'(?i)os\.path\.join\s*\([^)]*request',
            r'(?i)file_get_contents\s*\([^)]*\$',
        ],
        "message": "Potential path traversal vulnerability. Validate and sanitize file paths.",
        "severity": "high",
        "cwe": "CWE-22"
    },
    "unsafe_deserialization": {
        "patterns": [
            r'\bpickle\.loads?\s*\(',
            r'\byaml\.load\s*\([^)]*(?!Loader)',
            r'\bunserialize\s*\(',
            r'\bJSON\.parse\s*\([^)]*\)',
        ],
        "message": "Unsafe deserialization detected. Validate input before deserializing.",
        "severity": "high",
        "cwe": "CWE-502"
    },
    "command_injection": {
        "patterns": [
            r'\bos\.system\s*\(',
            r'\bsubprocess\.call\s*\(\s*[^[\]]',
            r'\bsubprocess\.Popen\s*\(\s*["\']',
            r'\bchild_process\.exec\s*\(',
            r'\bRuntime\.getRuntime\(\)\.exec\s*\(',
        ],
        "message": "Potential command injection. Use subprocess with shell=False and pass args as a list.",
        "severity": "critical",
        "cwe": "CWE-78"
    },
    "weak_crypto": {
        "patterns": [
            r'\bmd5\s*\(',
            r'\bsha1\s*\(',
            r'\bMD5\b',
            r'\bSHA1\b',
            r'hashlib\.md5',
            r'hashlib\.sha1',
        ],
        "message": "Weak cryptographic algorithm detected. Use SHA-256 or stronger.",
        "severity": "medium",
        "cwe": "CWE-327"
    },
    "debug_mode": {
        "patterns": [
            r'(?i)debug\s*=\s*True',
            r'(?i)DEBUG\s*=\s*1',
            r'(?i)app\.run\s*\([^)]*debug\s*=\s*True',
        ],
        "message": "Debug mode enabled. Disable in production.",
        "severity": "medium",
        "cwe": "CWE-489"
    },
    "insecure_random": {
        "patterns": [
            r'\brandom\.\w+\s*\(',
            r'\bMath\.random\s*\(',
        ],
        "message": "Insecure random number generator used. Use secrets module for security-sensitive operations.",
        "severity": "medium",
        "cwe": "CWE-330"
    },
}


def scan_security(code: str, language: str) -> List[SecurityIssue]:
    """Scan code for security vulnerabilities."""
    issues = []
    lines = code.split('\n')

    for category, config in SECURITY_PATTERNS.items():
        for pattern in config["patterns"]:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    # Skip if in a comment
                    stripped = line.strip()
                    if language in ('python',) and stripped.startswith('#'):
                        continue
                    if language in ('javascript', 'java', 'cpp') and stripped.startswith('//'):
                        continue

                    issues.append(SecurityIssue(
                        line=i,
                        message=f"[{category.upper()}] {config['message']}",
                        severity=config["severity"],
                        category=category,
                        cwe=config.get("cwe")
                    ))
                    break  # One issue per category per pattern match

    # Language-specific checks
    if language == "python":
        issues.extend(_python_specific_security(code, lines))
    elif language == "javascript":
        issues.extend(_javascript_specific_security(code, lines))

    return issues


def _python_specific_security(code: str, lines: list) -> List[SecurityIssue]:
    issues = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Check for assert used for validation (not security)
        if stripped.startswith('assert ') and any(kw in stripped.lower() for kw in ['password', 'auth', 'token', 'user']):
            issues.append(SecurityIssue(
                line=i,
                message="Don't use 'assert' for security checks. Assert statements are removed with -O flag.",
                severity="high",
                category="assert_security",
                cwe="CWE-617"
            ))

        # Check for tempfile without proper permissions
        if 'mktemp' in stripped:
            issues.append(SecurityIssue(
                line=i,
                message="Use 'mkstemp' instead of 'mktemp' to avoid race conditions.",
                severity="medium",
                category="race_condition",
                cwe="CWE-377"
            ))

    return issues


def _javascript_specific_security(code: str, lines: list) -> List[SecurityIssue]:
    issues = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Prototype pollution
        if re.search(r'__proto__|constructor\s*\[|Object\.assign\s*\(\s*\{\}', stripped):
            issues.append(SecurityIssue(
                line=i,
                message="Potential prototype pollution vulnerability.",
                severity="high",
                category="prototype_pollution",
                cwe="CWE-1321"
            ))

        # Regex DoS
        if re.search(r'new\s+RegExp\s*\([^)]*\+', stripped):
            issues.append(SecurityIssue(
                line=i,
                message="Dynamic regex construction from user input could lead to ReDoS attacks.",
                severity="medium",
                category="regex_dos",
                cwe="CWE-1333"
            ))

    return issues
