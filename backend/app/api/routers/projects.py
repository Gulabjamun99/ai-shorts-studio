import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any

from backend.app.core.database import get_db
from backend.app.models.schema import (
    DBProject, DBProjectVersion, DBContentTruth, DBScript, DBVideoSegment,
    DBVideoAssembly, DBQAResult, DBGenerationJob,
    CreateProjectRequest, SegmentApprovalItem
)
from backend.app.services.job_orchestrator import JobOrchestrator

router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.post("")
async def create_project(req: CreateProjectRequest):
    """
    Creates a new project, runs Concept Understanding,
    and returns Master Script with 3 segments for user approval.
    """
    try:
        res = await JobOrchestrator.create_project_and_script(
            title=req.title,
            concept=req.concept,
            platform=req.platform.value if hasattr(req.platform, "value") else str(req.platform),
            language=req.language,
            style=req.style.value if hasattr(req.style, "value") else str(req.style),
            voice_gender=req.voice_gender.value if hasattr(req.voice_gender, "value") else str(req.voice_gender),
            voice_tone=req.voice_tone,
            target_duration=req.target_duration,
            aspect_ratio=req.aspect_ratio,
            cta=req.cta or "Follow for more daily tips!"
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_projects(db: AsyncSession = Depends(get_db)):
    """Lists all user projects ordered by update timestamp."""
    res = await db.execute(select(DBProject).order_by(DBProject.updated_at.desc()))
    projects = res.scalars().all()
    out = []
    for p in projects:
        # Get latest version status
        q_v = await db.execute(
            select(DBProjectVersion).where(DBProjectVersion.project_id == p.id).order_by(DBProjectVersion.version_number.desc())
        )
        latest_v = q_v.scalars().first()
        out.append({
            "id": p.id,
            "title": p.title,
            "platform": p.platform,
            "language": p.language,
            "style": p.style,
            "voice_gender": p.voice_gender,
            "created_at": p.created_at.isoformat() if p.created_at else "",
            "latest_version_id": latest_v.id if latest_v else None,
            "status": latest_v.status if latest_v else "UNKNOWN"
        })
    return out


@router.get("/{project_id}")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves complete project details, versions, scripts, segments, assembly, and QA score."""
    p = await db.get(DBProject, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    q_v = await db.execute(
        select(DBProjectVersion).where(DBProjectVersion.project_id == project_id).order_by(DBProjectVersion.version_number.desc())
    )
    version = q_v.scalars().first()
    if not version:
        return {"project": p, "version": None}

    # Load script and segments
    q_s = await db.execute(select(DBScript).where(DBScript.version_id == version.id))
    script = q_s.scalars().first()
    q_segs = await db.execute(select(DBVideoSegment).where(DBVideoSegment.version_id == version.id).order_by(DBVideoSegment.segment_index))
    segs = q_segs.scalars().all()
    q_ass = await db.execute(select(DBVideoAssembly).where(DBVideoAssembly.version_id == version.id))
    assembly = q_ass.scalars().first()
    q_qa = await db.execute(select(DBQAResult).where(DBQAResult.version_id == version.id))
    qa = q_qa.scalars().first()
    q_job = await db.execute(select(DBGenerationJob).where(DBGenerationJob.version_id == version.id))
    job = q_job.scalars().first()

    return {
        "project": {
            "id": p.id,
            "title": p.title,
            "platform": p.platform,
            "language": p.language,
            "style": p.style,
            "voice_gender": p.voice_gender,
            "voice_tone": p.voice_tone,
            "target_duration": p.target_duration,
            "aspect_ratio": p.aspect_ratio
        },
        "version": {
            "id": version.id,
            "version_number": version.version_number,
            "raw_concept": version.raw_concept,
            "status": version.status
        },
        "script": {
            "master_script": script.master_script if script else "",
            "estimated_duration": script.estimated_duration if script else 22.0,
            "is_approved": script.is_approved if script else False
        } if script else None,
        "segments": [
            {
                "segment_index": s.segment_index,
                "duration_sec": s.duration_sec,
                "narration": s.narration,
                "visual_prompt": s.visual_prompt,
                "on_screen_text": s.on_screen_text,
                "status": s.status
            } for s in segs
        ],
        "assembly": {
            "final_video_url": f"/storage/videos/{Path(assembly.final_video_path).name}" if (assembly and assembly.final_video_path) else None,
            "subtitles_url": f"/storage/subtitles/{Path(assembly.subtitles_path).name}" if (assembly and assembly.subtitles_path) else None,
            "resolution": assembly.resolution if assembly else "",
            "duration_sec": assembly.duration_sec if assembly else 0.0,
            "status": assembly.status if assembly else ""
        } if assembly else None,
        "qa": {
            "overall_score": qa.overall_score if qa else None,
            "passed": qa.passed if qa else False,
            "categories": json.loads(qa.category_scores) if qa and qa.category_scores else {},
            "failure_reasons": json.loads(qa.failure_reasons) if qa and qa.failure_reasons else []
        } if qa else None,
        "job": {
            "id": job.id if job else None,
            "current_state": job.current_state if job else None,
            "progress_pct": job.progress_pct if job else 0,
            "error_message": job.error_message if job else None
        } if job else None
    }
