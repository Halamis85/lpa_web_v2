from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_db, get_current_user
from ..models import Line, User

router = APIRouter()

@router.get("/")
def list_lines(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    return db.query(Line).all()


@router.post("/")
def create_line(
    name: str,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    existing = db.query(Line).filter(Line.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Line already exists")

    line = Line(name=name)
    db.add(line)
    db.commit()
    db.refresh(line)

    return {"id": line.id, "name": line.name}
