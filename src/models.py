"""Pydantic models for API request and response validation."""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────

class LanguageEnum(str, Enum):
    TAMIL = "Tamil"
    HINDI = "Hindi"


class PaymentPreference(str, Enum):
    EMI = "EMI"
    FULL_PAYMENT = "FULL_PAYMENT"
    PARTIAL_PAYMENT = "PARTIAL_PAYMENT"
    DOWN_PAYMENT = "DOWN_PAYMENT"


class RejectionReason(str, Enum):
    HIGH_INTEREST = "HIGH_INTEREST"
    BUDGET_CONSTRAINTS = "BUDGET_CONSTRAINTS"
    ALREADY_PAID = "ALREADY_PAID"
    NOT_INTERESTED = "NOT_INTERESTED"
    NONE = "NONE"


class AdherenceStatus(str, Enum):
    FOLLOWED = "FOLLOWED"
    NOT_FOLLOWED = "NOT_FOLLOWED"


class SentimentEnum(str, Enum):
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"


# ── Request ────────────────────────────────────────────────────────────

class CallAnalyticsRequest(BaseModel):
    """Incoming API request body."""
    language: str = Field(..., description="Tamil (Tanglish) or Hindi (Hinglish)")
    audioFormat: str = Field(default="mp3", description="Audio format, always mp3")
    audioBase64: str = Field(..., description="Base64-encoded MP3 audio")


# ── Response sub-models ────────────────────────────────────────────────

class SOPValidation(BaseModel):
    """SOP adherence breakdown."""
    greeting: bool = Field(..., description="Agent started with a greeting")
    identification: bool = Field(..., description="Agent identified self / verified customer")
    problemStatement: bool = Field(..., description="Purpose of call was stated")
    solutionOffering: bool = Field(..., description="Agent offered a solution")
    closing: bool = Field(..., description="Agent properly closed the call")
    complianceScore: float = Field(..., ge=0.0, le=1.0, description="Ratio of SOP steps followed")
    adherenceStatus: str = Field(..., description="FOLLOWED or NOT_FOLLOWED")
    explanation: str = Field(..., description="Brief explanation of compliance")


class Analytics(BaseModel):
    """Business intelligence extracted from the call."""
    paymentPreference: str = Field(..., description="EMI, FULL_PAYMENT, PARTIAL_PAYMENT, or DOWN_PAYMENT")
    rejectionReason: str = Field(..., description="Reason for rejection or NONE")
    sentiment: str = Field(..., description="Positive, Negative, or Neutral")


class CallAnalyticsResponse(BaseModel):
    """Complete API response."""
    status: str = Field(default="success")
    language: str
    transcript: str
    summary: str
    sop_validation: SOPValidation
    analytics: Analytics
    keywords: List[str]
