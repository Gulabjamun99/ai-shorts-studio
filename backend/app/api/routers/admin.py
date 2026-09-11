from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from pathlib import Path

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.schema import DBProject, DBGenerationJob, DBQAResult

router = APIRouter(prefix="/api/admin", tags=["Admin & Observability"])

@router.get("/metrics")
async def get_system_metrics(db: AsyncSession = Depends(get_db)):
    """
    Returns platform-wide operational health metrics:
    total projects, generation jobs, failure rate, QA pass rate, and storage usage.
    """
    total_projects = await db.scalar(select(func.count(DBProject.id))) or 0
    total_jobs = await db.scalar(select(func.count(DBGenerationJob.id))) or 0
    completed_jobs = await db.scalar(
        select(func.count(DBGenerationJob.id)).where(DBGenerationJob.current_state == "READY")
    ) or 0
    failed_jobs = await db.scalar(
        select(func.count(DBGenerationJob.id)).where(DBGenerationJob.current_state == "FAILED")
    ) or 0

    qa_total = await db.scalar(select(func.count(DBQAResult.id))) or 0
    qa_passed = await db.scalar(select(func.count(DBQAResult.id)).where(DBQAResult.passed == True)) or 0
    qa_avg_score = await db.scalar(select(func.avg(DBQAResult.overall_score))) or 0.0

    # Calculate total storage size in MB
    total_storage_bytes = 0
    for p in settings.STORAGE_DIR.rglob("*"):
        if p.is_file():
            total_storage_bytes += p.stat().st_size
    storage_mb = round(total_storage_bytes / (1024 * 1024), 2)

    return {
        "total_projects": total_projects,
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "success_rate_pct": round((completed_jobs / total_jobs * 100.0) if total_jobs > 0 else 100.0, 1),
        "qa_records": qa_total,
        "qa_passed": qa_passed,
        "qa_pass_rate_pct": round((qa_passed / qa_total * 100.0) if qa_total > 0 else 100.0, 1),
        "qa_avg_score": round(float(qa_avg_score), 1),
        "storage_usage_mb": storage_mb,
        "active_provider": settings.DEFAULT_VIDEO_PROVIDER,
        "default_model": settings.VEO_MODEL
    }
