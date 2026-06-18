from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database import Base


class Pick(Base):
    __tablename__ = "picks"

    id = Column(Integer, primary_key=True, index=True)
    match = Column(String, nullable=False)
    market = Column(String, nullable=False)
    selection = Column(String, nullable=False)
    model_probability = Column(Float, nullable=False)
    best_odds = Column(Float, nullable=False)
    expected_value = Column(Float, nullable=False)
    confidence = Column(Integer, nullable=False)
    reasoning = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    result_status = Column(String, nullable=True, default="pending")
    result_odds = Column(Float, nullable=True)
