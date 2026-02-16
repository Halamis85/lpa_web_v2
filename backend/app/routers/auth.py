from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..auth import (
    get_db,
    verify_password,
    create_access_token,
    get_current_user,
    hash_password,
)
from ..models import User

router = APIRouter()


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Přihlášení uživatele

    Vrací:
        - access_token: JWT token
        - token_type: "bearer"
        - force_password_change: True pokud je vyžadována změna hesla
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    if (
        not user
        or not user.password_hash
        or not verify_password(form_data.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Kontrola aktivního účtu
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Účet je deaktivován. Kontaktujte administrátora.",
        )

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "force_password_change": user.force_password_change,  # Příznak pro změnu hesla
        "user": {
            "id": user.id,
            "jmeno": user.jmeno,
            "email": user.email,
            "role": user.role,
            "roles": user.get_roles_list(),
        },
    }


@router.get("/me")
def who_am_i(current: User = Depends(get_current_user)):
    """Vrátí informace o aktuálně přihlášeném uživateli"""
    return {
        "id": current.id,
        "email": current.email,
        "jmeno": current.jmeno,
        "role": current.role,
        "roles": current.get_roles_list(),
        "force_password_change": current.force_password_change,
    }


@router.post("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Změna hesla aktuálně přihlášeného uživatele

    Args:
        password_data: Staré a nové heslo
    """
    # Ověř staré heslo
    if not verify_password(password_data.old_password, current.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Staré heslo je nesprávné",
        )

    # Validace nového hesla
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nové heslo musí mít alespoň 6 znaků",
        )

    # Aktualizuj heslo
    current.password_hash = hash_password(password_data.new_password)
    current.force_password_change = False  # Už není potřeba měnit heslo
    db.commit()

    return {
        "status": "ok",
        "message": "Heslo bylo úspěšně změněno",
    }
