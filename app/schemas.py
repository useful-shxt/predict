from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class PickCreate(BaseModel):
    """Schema for creating a new pick."""
    match: str
    market: str
    selection: str
    model_probability: float = Field(..., ge=0, le=1, description="Probability between 0 and 1")
    best_odds: float
    expected_value: float
    confidence: int = Field(..., ge=0, le=100, description="Confidence between 0 and 100")
    reasoning: Optional[str] = None


class PickResponse(BaseModel):
    """Schema for returning a pick."""
    id: int
    match: str
    market: str
    selection: str
    model_probability: float
    best_odds: float
    expected_value: float
    confidence: int
    reasoning: Optional[str]
    published_at: datetime
    result_status: Optional[str]
    result_odds: Optional[float]

    model_config = ConfigDict(from_attributes=True)
