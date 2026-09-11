import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.core.config import settings
from backend.app.core.security import validate_image_file
from backend.app.core.database import get_db
from backend.app.models.schema import DBAsset, DBProject

router = APIRouter(prefix="/api/assets", tags=["Assets"])

@router.post("/upload")
async def upload_asset(
    project_id: str = Form(...),
    asset_type: str = Form("LOGO"),  # LOGO, PRODUCT, CHARACTER_REF, SCREENSHOT
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Validates and stores user-uploaded brand logo, product image,
    or reference asset securely.
    """
    project = await db.get(DBProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}"
        )

    file_id = uuid.uuid4().hex[:8]
    save_path = settings.ASSETS_DIR / f"asset_{file_id}{ext}"

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    # Validate image integrity
    is_valid, msg = validate_image_file(save_path)
    if not is_valid:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=msg)

    asset = DBAsset(
        id=str(uuid.uuid4()),
        project_id=project_id,
        asset_type=asset_type.upper(),
        file_path=str(save_path),
        original_filename=file.filename
    )
    db.add(asset)
    await db.commit()

    return {
        "status": "SUCCESS",
        "asset_id": asset.id,
        "asset_type": asset.asset_type,
        "file_url": f"/storage/assets/{save_path.name}"
    }


@router.get("/{project_id}")
async def list_project_assets(project_id: str, db: AsyncSession = Depends(get_db)):
    """Lists all uploaded assets associated with a project."""
    res = await db.execute(select(DBAsset).where(DBAsset.project_id == project_id))
    assets = res.scalars().all()
    return [
        {
            "id": a.id,
            "asset_type": a.asset_type,
            "filename": a.original_filename,
            "file_url": f"/storage/assets/{Path(a.file_path).name}",
            "created_at": a.created_at.isoformat() if a.created_at else ""
        }
        for a in assets
    ]
