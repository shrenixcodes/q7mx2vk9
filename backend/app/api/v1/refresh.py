from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_analysis_service
from app.api.v1.schemas import RefreshResponse
from app.services.analysis_service import AnalysisService, DataUnavailableError, RefreshThrottledError

router = APIRouter(tags=["refresh"])


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    service: AnalysisService = Depends(get_analysis_service),
) -> RefreshResponse:
    """Bounded refresh of the configured analysis range. Rate-limited to one
    attempt per cooldown window so this public endpoint cannot be used to
    drive uncontrolled repeated upstream requests.
    """
    try:
        await service.refresh()
    except RefreshThrottledError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except DataUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return RefreshResponse(status="ok", loaded_at=service.loaded_at)
