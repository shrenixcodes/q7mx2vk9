from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness only. Never depends on a live Elexon request."""
    return {"status": "ok", "version": "0.1.0"}
