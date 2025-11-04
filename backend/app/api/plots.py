from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/plots", tags=["plots"])


@router.get("/", summary="Plot management endpoints are under construction.")
async def list_plots():
    try:
        return {"message": "Plot management endpoints are under construction."}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
