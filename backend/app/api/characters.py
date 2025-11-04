from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.get("/", summary="Character management endpoints are under construction.")
async def list_characters():
    try:
        return {"message": "Character management endpoints are under construction."}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
