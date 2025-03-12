from fastapi import APIRouter, Depends

# from app.schemas.user import UserCreate, UserRead, ...
# from app.core.dependencies import get_db, ...
# from app.models.user import User

router = APIRouter(prefix="/sets", tags=["sets"])


@router.post("/analyze-records")
async def analyze_records():
    return {"message": "Analyze records"}


@router.post("/create-event-map")
async def create_event_map():
    return {"message": "Create event map"}
