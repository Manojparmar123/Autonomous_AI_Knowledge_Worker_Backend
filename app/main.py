# from fastapi import FastAPI, Depends, HTTPException, Query, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import JSONResponse
# from sqlmodel import Session, select
# import json

# # Import your internal modules
# from .db import init_db, get_session
# from .models import Document, Task, Run, Insight, Report
# from .schemas import IngestRequest, RunResponse
# from .auth import current_user
# from .config import APP_ENV
# from .upload_api import router as upload_router
# from .rag_api import router as rag_router
# from .dashboard_api import router as dashboard_router
# from .scheduler import start_scheduler, run_manual_job, scheduler, JOB_REGISTRY
# from .auth_routes import router as auth_router

# app = FastAPI(title="AI Worker", version="0.1.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     errors = [{"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in exc.errors()]
#     return JSONResponse(status_code=422, content={"detail": errors})

# @app.exception_handler(Exception)
# async def generic_exception_handler(request: Request, exc: Exception):
#     return JSONResponse(status_code=500, content={"detail": str(exc)})

# # ✅ Include routers without prefix duplication
# app.include_router(rag_router)  # Already has /rag prefix inside rag_api.py
# app.include_router(upload_router, prefix="/upload", tags=["Upload API"])
# app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
# app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# @app.on_event("startup")
# def startup_event():
#     init_db()
#     start_scheduler()

# @app.get("/health")
# def health():
#     return {"ok": True, "env": APP_ENV}

# @app.post("/ingest/run", response_model=RunResponse)
# def ingest_run(
#     req: IngestRequest,
#     user=Depends(current_user),
#     session: Session = Depends(get_session)
# ):
#     run = Run(status="running", state_log=json.dumps([{"event": "enqueued"}]))
#     session.add(run)
#     session.commit()
#     session.refresh(run)

#     task_payload = json.dumps({
#         "source": req.source,
#         "query": req.query,
#         "params": req.params
#     })

#     task = Task(kind="ingest", payload=task_payload, run_id=run.id)
#     session.add(task)
#     session.commit()
#     session.refresh(task)

#     from .workers import inline_ingest
#     inline_ingest(task.id, session)

#     return {"task_id": task.id}

# @app.get("/runs")
# def list_runs(
#     limit: int = Query(10, ge=1, le=100),
#     offset: int = Query(0, ge=0),
#     session: Session = Depends(get_session)
# ):
#     order_field = Run.created_at if hasattr(Run, "created_at") else Run.id
#     query = select(Run).order_by(order_field.desc()).offset(offset).limit(limit)
#     runs = session.exec(query).all()
#     result = []
#     for run in runs:
#         result.append({
#             "id": run.id,
#             "task_id": run.task_id,
#             "status": run.status,
#             "log": json.loads(run.state_log or "[]"),
#             "created_at": getattr(run, "created_at", None),
#             "finished_at": getattr(run, "finished_at", None)
#         })
#     return result

# @app.get("/insights")
# def list_insights(
#     limit: int = Query(10, ge=1, le=100),
#     offset: int = Query(0, ge=0),
#     session: Session = Depends(get_session)
# ):
#     query = select(Insight).order_by(Insight.created_at.desc()).offset(offset).limit(limit)
#     insights = session.exec(query).all()
#     return insights

# @app.get("/reports")
# def list_reports(
#     kind: str | None = None,
#     search: str | None = None,
#     session: Session = Depends(get_session)
# ):
#     query = select(Report).order_by(Report.created_at.desc())
#     if kind:
#         query = query.where(Report.kind == kind)
#     reports = session.exec(query).all()
#     if search:
#         reports = [r for r in reports if search.lower() in (r.content or "").lower()]
#     return reports

# @app.post("/scheduler/run-now")
# def trigger_all_jobs():
#     results = []
#     for job_name in JOB_REGISTRY.keys():
#         try:
#             run_manual_job(job_name)
#             results.append({"job": job_name, "status": "triggered"})
#         except ValueError as e:
#             results.append({"job": job_name, "status": "failed", "error": str(e)})
#     return {"results": results}

# @app.get("/scheduler/jobs")
# def list_scheduler_jobs():
#     jobs = []
#     for job in scheduler.get_jobs():
#         jobs.append({
#             "id": job.id,
#             "name": job.name,
#             "next_run": str(job.next_run_time) if job.next_run_time else None
#         })
#     return {
#         "registered": list(JOB_REGISTRY.keys()),
#         "scheduled": jobs
#     }

# @app.get("/chat")
# def chat():
#     return {"message": "Chat endpoint is working!"}


from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
import asyncio
import json

# Internal modules
from .db import get_session, DATABASE_URL, async_init_db
from .models import Document, Task, Run, Insight, Report
from .schemas import IngestRequest, RunResponse
from .auth import current_user
from .config import APP_ENV
from .upload_api import router as upload_router
from .rag_api import router as rag_router
from .dashboard_api import router as dashboard_router
from .scheduler import start_scheduler, run_manual_job, scheduler, JOB_REGISTRY
from .auth_routes import router as auth_router

app = FastAPI(title="AI Worker", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})

# Include routers
app.include_router(rag_router)
app.include_router(upload_router, prefix="/upload", tags=["Upload API"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# ------------------- Async-safe Startup -------------------
@app.on_event("startup")
async def startup_event():
    # Async DB init to avoid "greenlet_spawn" issues with aiosqlite
    await async_init_db()
    # Scheduler can stay sync
    start_scheduler()
# -----------------------------------------------------------

@app.get("/health")
def health():
    return {"ok": True, "env": APP_ENV}

@app.post("/ingest/run", response_model=RunResponse)
def ingest_run(
    req: IngestRequest,
    user=Depends(current_user),
    session: Session = Depends(get_session)
):
    run = Run(status="running", state_log=json.dumps([{"event": "enqueued"}]))
    session.add(run)
    session.commit()
    session.refresh(run)

    task_payload = json.dumps({
        "source": req.source,
        "query": req.query,
        "params": req.params
    })

    task = Task(kind="ingest", payload=task_payload, run_id=run.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    from .workers import inline_ingest
    inline_ingest(task.id, session)

    return {"task_id": task.id}

@app.get("/runs")
def list_runs(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    order_field = Run.created_at if hasattr(Run, "created_at") else Run.id
    query = select(Run).order_by(order_field.desc()).offset(offset).limit(limit)
    runs = session.exec(query).all()
    return [
        {
            "id": run.id,
            "task_id": run.task_id,
            "status": run.status,
            "log": json.loads(run.state_log or "[]"),
            "created_at": getattr(run, "created_at", None),
            "finished_at": getattr(run, "finished_at", None)
        }
        for run in runs
    ]

@app.get("/insights")
def list_insights(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    query = select(Insight).order_by(Insight.created_at.desc()).offset(offset).limit(limit)
    return session.exec(query).all()

@app.get("/reports")
def list_reports(
    kind: str | None = None,
    search: str | None = None,
    session: Session = Depends(get_session)
):
    query = select(Report).order_by(Report.created_at.desc())
    if kind:
        query = query.where(Report.kind == kind)
    reports = session.exec(query).all()
    if search:
        reports = [r for r in reports if search.lower() in (r.content or "").lower()]
    return reports

@app.post("/scheduler/run-now")
def trigger_all_jobs():
    results = []
    for job_name in JOB_REGISTRY.keys():
        try:
            run_manual_job(job_name)
            results.append({"job": job_name, "status": "triggered"})
        except ValueError as e:
            results.append({"job": job_name, "status": "failed", "error": str(e)})
    return {"results": results}

@app.get("/scheduler/jobs")
def list_scheduler_jobs():
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None
        })
    return {"registered": list(JOB_REGISTRY.keys()), "scheduled": jobs}

@app.get("/chat")
def chat():
    return {"message": "Chat endpoint is working!"}
