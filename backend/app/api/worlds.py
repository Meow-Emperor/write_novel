from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/worlds", tags=["worlds"])


@router.get("/", summary="World settings endpoints are under construction.")
async def list_worlds():
    try:
        return {"message": "World settings endpoints are under construction."}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
