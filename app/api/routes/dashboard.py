from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from app.db.session import get_db
from app.services.dashboard import DashboardService

router = APIRouter()

@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    service = DashboardService(db)
    return await service.get_stats()
