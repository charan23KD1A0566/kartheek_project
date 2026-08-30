from pydantic import BaseModel, Field, EmailStr, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============ Enums ============

class ReportType(str, Enum):
    NEAR_MISS = "near_miss"
    UNSAFE_ACT = "unsafe_act"
    UNSAFE_CONDITION = "unsafe_condition"


class SIFStatus(str, Enum):
    YES = "YES"
    NO = "NO"
    UNCERTAIN = "UNCERTAIN"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    SAFETY_OFFICER = "SAFETY_OFFICER"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"


class ValidationDecision(str, Enum):
    AGREE = "AGREE"
    DISAGREE = "DISAGREE"
    MODIFY = "MODIFY"


class ModelType(str, Enum):
    RULE_ENGINE = "RULE_ENGINE"
    TFIDF_LOGISTIC = "TFIDF_LOGISTIC"
    LLM = "LLM"
    HYBRID = "HYBRID"


# ============ Auth Models ============

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.EMPLOYEE

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    role: UserRole


# ============ Report Models ============

class SafetyReportCreate(BaseModel):
    report_text: str = Field(..., min_length=10, max_length=10000)
    report_type: ReportType = ReportType.NEAR_MISS
    location: Optional[str] = None
    department: Optional[str] = None
    activity: Optional[str] = None
    date: Optional[datetime] = None


class SafetyReportUpdate(BaseModel):
    report_text: Optional[str] = Field(default=None, min_length=10, max_length=10000)
    report_type: Optional[ReportType] = None
    location: Optional[str] = None
    department: Optional[str] = None
    activity: Optional[str] = None
    date: Optional[datetime] = None


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=10000)
    report_type: ReportType = ReportType.NEAR_MISS
    location: Optional[str] = None


class SafetyReport(SafetyReportCreate):
    report_id: str
    data_source: str = "USER_SUBMISSION"
    created_at: datetime
    updated_at: Optional[datetime] = None


# ============ AI Prediction Models ============

class AIAnalysisResult(BaseModel):
    sif_status: SIFStatus
    sif_probability: float = Field(..., ge=0, le=1)
    confidence: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    hazards: List[str] = []
    exposure: List[str] = []
    control_failures: List[str] = []
    evidence: List[str] = []
    explanation: str
    recommendation: str
    safety_action_plan: Dict[str, List[str]] = {}
    model_type: ModelType = ModelType.RULE_ENGINE
    model_version: str = "1.0"


class AIPrediction(AIAnalysisResult):
    prediction_id: str
    report_id: str
    created_at: datetime


# ============ Validation Models ============

class HumanValidationInput(BaseModel):
    ai_decision: SIFStatus
    human_decision: ValidationDecision
    modified_sif_status: Optional[SIFStatus] = None
    modified_risk_level: Optional[RiskLevel] = None
    comments: Optional[str] = None


class HumanValidation(HumanValidationInput):
    validation_id: str
    report_id: str
    reviewer: str
    timestamp: datetime


# ============ Dashboard Models ============

class DashboardStats(BaseModel):
    total_reports: int
    potential_sif_precursors: int
    high_risk_reports: int
    critical_risk_reports: int
    pending_validation: int
    validated_reports: int
    validation_agreement_rate: float


class DashboardData(BaseModel):
    stats: DashboardStats
    recent_reports: List[SafetyReport] = []


# ============ Analytics Models ============

class HazardDistribution(BaseModel):
    hazard: str
    count: int
    percentage: float


class AnalyticsData(BaseModel):
    total_reports: int
    sif_percentage: float
    risk_distribution: Dict[str, int]
    hazard_distribution: List[HazardDistribution]
    validation_agreement: float
    data_source_distribution: Dict[str, int]
    reports_over_time: List[Dict[str, Any]]


# ============ Taxonomy Models ============

class TaxonomyCategory(BaseModel):
    name: str
    description: str
    keywords: List[str]
    subcategories: List[str] = []


class TaxonomyData(BaseModel):
    categories: Dict[str, TaxonomyCategory]
    last_updated: datetime


# ============ API Response Models ============

class HealthResponse(BaseModel):
    status: str = "healthy"
    database: str = "connected"
    version: str = "1.0"


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: str = "ERROR"


# ============ Batch Upload Models ============

class UploadResponse(BaseModel):
    file_name: str
    total_records: int
    processed_records: int
    skipped_records: int
    errors: List[str] = []
    preview: List[SafetyReport] = []


class UploadStatusResponse(BaseModel):
    upload_id: str
    status: str  # processing, completed, failed
    processed: int
    total: int
    progress_percent: float
