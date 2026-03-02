from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"


class CodeSubmission(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000)
    language: Language = Language.PYTHON
    filename: Optional[str] = "untitled"


class SyntaxError_(BaseModel):
    line: int
    column: int
    message: str
    severity: str = "error"


class LogicalWarning(BaseModel):
    line: Optional[int] = None
    message: str
    severity: str = "warning"
    category: str = "logic"


class SecurityIssue(BaseModel):
    line: Optional[int] = None
    message: str
    severity: str = "high"
    category: str = "security"
    cwe: Optional[str] = None


class RefactoringSuggestion(BaseModel):
    line: Optional[int] = None
    message: str
    category: str
    priority: str = "medium"
    suggestion: Optional[str] = None


class CodeSmell(BaseModel):
    line: Optional[int] = None
    message: str
    smell_type: str
    severity: str = "medium"


class PerformanceAlert(BaseModel):
    line: Optional[int] = None
    message: str
    risk_level: str = "medium"
    category: str = "performance"


class AnalysisResponse(BaseModel):
    syntax_errors: List[SyntaxError_] = []
    logical_warnings: List[LogicalWarning] = []
    time_complexity: str = "O(1)"
    space_complexity: str = "O(1)"
    clean_code_score: float = 0
    cyclomatic_complexity: int = 0
    similarity_score: float = 0
    security_issues: List[SecurityIssue] = []
    refactoring_suggestions: List[RefactoringSuggestion] = []
    code_smells: List[CodeSmell] = []
    maintainability_index: float = 0
    readability_score: float = 0
    performance_alerts: List[PerformanceAlert] = []
    loc: int = 0
    comment_ratio: float = 0
    function_count: int = 0
    ai_explanation: Optional[str] = None
    analysis_time_ms: float = 0
    language: str = "python"


class HistoryEntry(BaseModel):
    id: Optional[str] = None
    code: str
    language: str
    filename: str
    analysis: AnalysisResponse
    created_at: datetime = Field(default_factory=datetime.utcnow)
