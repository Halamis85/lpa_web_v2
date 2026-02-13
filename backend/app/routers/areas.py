from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_db, get_current_user
from ..models import Area, User

router = APIRouter()

@router.post("/")
def create_area(
    name: str,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    existing = db.query(Area).filter(Area.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Area already exists")

    area = Area(name=name)
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


@router.get("/")
def list_areas(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Area).all()
