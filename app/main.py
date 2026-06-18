import os
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app.models import Pick
from app.schemas import PickCreate, PickResponse

# Auto-create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Predict API", version="1.0.0")

# Read admin secret from environment
ADMIN_SECRET = os.getenv("ADMIN_SECRET")


def verify_admin_secret(x_admin_secret: str | None = Header(None, alias="X-Admin-Secret")):
    """Verify the X-Admin-Secret header matches the environment variable."""
    if not ADMIN_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: ADMIN_SECRET not set"
        )
    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing X-Admin-Secret header"
        )
    return True


@app.get("/api/pick/today", response_model=PickResponse)
def get_pick_today(db: Session = Depends(get_db)):
    """
    Get the most recent pick published today.
    Returns 404 if no pick exists for today.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    pick = (
        db.query(Pick)
        .filter(Pick.published_at >= today_start)
        .order_by(Pick.published_at.desc())
        .first()
    )

    if not pick:
        raise HTTPException(
            status_code=404,
            detail="No pick published today."
        )

    return pick


@app.get("/api/picks/recent", response_model=list[PickResponse])
def get_recent_picks(limit: int = 30, db: Session = Depends(get_db)):
    """
    Get recent picks ordered by published_at descending.
    Limit is capped at 100.
    """
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 1

    picks = (
        db.query(Pick)
        .order_by(Pick.published_at.desc())
        .limit(limit)
        .all()
    )

    return picks


@app.post("/api/picks", response_model=PickResponse, status_code=201)
def create_pick(
    pick_data: PickCreate,
    db: Session = Depends(get_db),
    admin_verified: bool = Depends(verify_admin_secret)
):
    """
    Create a new pick. Protected by X-Admin-Secret header.
    Automatically sets published_at to now and result_status to 'pending'.
    """
    new_pick = Pick(
        match=pick_data.match,
        market=pick_data.market,
        selection=pick_data.selection,
        model_probability=pick_data.model_probability,
        best_odds=pick_data.best_odds,
        expected_value=pick_data.expected_value,
        confidence=pick_data.confidence,
        reasoning=pick_data.reasoning,
        published_at=datetime.now(timezone.utc),
        result_status="pending"
    )
    db.add(new_pick)
    db.commit()
    db.refresh(new_pick)
    return new_pick


@app.get("/health")
def health_check():
    """Simple health check for Railway."""
    return {"status": "ok"}
