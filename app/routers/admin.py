from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.seeder import seed_demo_data

router = APIRouter(prefix="/api/v1/admin", tags=["Admin & Demonstration Seeder"])


@router.post(
    "/seed-demo-data",
    status_code=status.HTTP_201_CREATED,
    summary="Seed pitch-ready demonstration cohort including Patient AIIA-P089 and SPC drift",
)
async def seed_demo(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    return await seed_demo_data(db)
