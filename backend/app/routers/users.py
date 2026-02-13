from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_db, hash_password, get_current_user
from ..models import User

router = APIRouter()

@router.post("/create-first-admin")
def create_first_admin(db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == "admin@lpa.local").first()
    if existing:
        return {"status": "exists", "message": "Admin už existuje"}

    admin = User(
        jmeno="Admin",
        email="admin@lpa.local",
        role="admin",
        password_hash=hash_password("admin")
    )
    db.add(admin)
    db.commit()
    return {"status": "created", "message": "Admin vytvořen (heslo = admin)"}


@router.get("/")
def list_users(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    return db.query(User).all()


@router.post("/")
def create_user(
    jmeno: str,
    email: str,
    role: str = "auditor",
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    u = User(jmeno=jmeno, email=email, role=role)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.patch("/{user_id}/role")
def change_user_role(
    user_id: int,
    role: str,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    u.role = role
    db.commit()
    db.refresh(u)
    return u


@router.post("/init-passwords")
def init_passwords(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    users = db.query(User).all()
    for u in users:
        if u.email and not u.password_hash:
            u.password_hash = hash_password(u.email)

    db.commit()
    return {"status": "ok", "message": "Hesla inicializována (dočasně = email)."}
