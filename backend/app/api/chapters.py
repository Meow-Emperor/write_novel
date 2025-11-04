from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/chapters", tags=["chapters"])


@router.get("/", summary="Chapter management endpoints are under construction.")
async def list_chapters():
    try:
        return {"message": "Chapter management endpoints are under construction."}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
