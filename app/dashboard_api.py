# apps/backend/app/dashboard_api.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select
from datetime import datetime
import uuid
import logging

from .db import get_session
from .models import Run, Report
from .scheduler import scheduler, scheduled_news_summary, scheduled_stock_check, scheduled_google_trends

logger = logging.getLogger("dashboard_api")
logger.setLevel(logging.INFO)

router = APIRouter(tags=["dashboard"])


# -------------------------
# Logs Endpoint
# -------------------------
@router.get("/logs")
def logs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    job_type: str | None = Query(None, description="Filter by job_type"),
    session: Session = Depends(get_session)
):
    log_entries = []

    # Get Runs
    runs = session.exec(select(Run).order_by(Run.started_at.desc())).all()
    for run in runs:
        log_entries.append({
            "id": run.id,
            "status": run.status,
            "job_type": run.job_type,
            "created_at": run.started_at.isoformat() if run.started_at else None,
        })

    # Get Reports
    reports = session.exec(select(Report).order_by(Report.created_at.desc())).all()
    for r in reports:
        log_entries.append({
            "id": r.id,
            "status": "completed",
            "job_type": f"{r.kind}_report",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    # Filter by job_type if provided
    if job_type:
        log_entries = [log for log in log_entries if log["job_type"] == job_type]

    # Sort by date
    log_entries.sort(key=lambda x: x["created_at"] or "", reverse=True)

    # Apply offset + limit
    paginated = log_entries[offset: offset + limit]

    return {
        "items": paginated,
        "limit": limit,
        "offset": offset,
        "total": len(log_entries),
    }


# -------------------------
# Insights Endpoint
# -------------------------
@router.get("/insights")
def insights(
    q: str = Query("", description="Search query (optional, matches kind)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    session: Session = Depends(get_session)
):
    reports = session.exec(select(Report).order_by(Report.created_at.asc())).all()

    if q:
        reports = [r for r in reports if q.lower() in (r.kind or "").lower()]

    insights_dict = {}
    for r in reports:
        if not r.created_at:
            continue
        day = r.created_at.strftime("%Y-%m-%d")
        insights_dict[day] = insights_dict.get(day, 0) + 1

    sorted_dates = sorted(insights_dict.keys())
    data = [{"date": day, "value": insights_dict[day]} for day in sorted_dates]

    start = (page - 1) * page_size
    end = start + page_size
    paginated = data[start:end]

    return {
        "items": paginated,
        "page": page,
        "page_size": page_size,
        "total": len(data),
    }


# -------------------------
# Request New Task Endpoint
# -------------------------
@router.post("/request-task")
def request_task(
    task_type: str = Query(..., description="Type: news, stock, trends"),
    session: Session = Depends(get_session)
):
    job_map = {
        "news": scheduled_news_summary,
        "stock": scheduled_stock_check,
        "trends": scheduled_google_trends,
    }

    if task_type not in job_map:
        raise HTTPException(status_code=400, detail="Invalid task_type")

    # Schedule job to run once immediately
    scheduler.add_job(job_map[task_type], trigger="date")
    logger.info(f"Scheduled one-time {task_type} job via /request-task")

    # Log into DB with UUID
    run = Run(
        id=str(uuid.uuid4()),  # ensure unique UUID
        job_type=task_type,
        status="scheduled",
        started_at=datetime.utcnow()
    )
    session.add(run)
    session.commit()
    logger.info(f"Logged new run {run.id} for task {task_type}")

    return {"status": "success", "message": f"{task_type} task requested"}
