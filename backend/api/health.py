from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    """Used to check the server is up (and to wake it from sleep on free hosting)."""
    return {"status": "ok"}
