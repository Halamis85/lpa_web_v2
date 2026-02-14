from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import secrets
import string

from ..auth import get_db, hash_password, get_current_user
from ..models import User
from ..email_service import send_password_reset_email

router = APIRouter()


# Endpoint pro vytvoření prvního admina, pokud ještě neexistuje
def generate_random_password(length: int = 12) -> str:
    """Vygeneruje náhodné heslo"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password


@router.post("/create-first-admin")
def create_first_admin(db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == "admin@lpa.local").first()
    if existing:
        return {"status": "exists", "message": "Admin už existuje"}

    admin = User(
        jmeno="Admin",
        email="admin@lpa.local",
        role="admin",
        password_hash=hash_password("admin"),
    )
    db.add(admin)
    db.commit()
    return {"status": "created", "message": "Admin vytvořen (heslo = admin)"}


@router.get("")
def list_users(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    return db.query(User).all()


@router.post("")
def create_user(
    jmeno: str,
    email: str,
    role: str = "auditor",
    send_email: bool = True,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Vytvoří nového uživatele a odešle mu email s přístupovými údaji

    Args:
        jmeno: Jméno uživatele
        email: Email uživatele
        role: Role (auditor, solver, admin)
        send_email: Zda poslat email s heslem (výchozí True)
    """
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Vygeneruj náhodné heslo
    password = generate_random_password()
    u = User(jmeno=jmeno, email=email, role=role, password_hash=hash_password(password))
    db.add(u)
    db.commit()
    db.refresh(u)

    if send_email:
        try:
            send_password_reset_email(
                to_email=email, user_name=jmeno, new_password=password, is_new_user=True
            )
        except Exception as e:
            print(f"Chyba při odesílání emailu: {e}")
            # I když selže email, uživatel je vytvořen

    return {
        "id": u.id,
        "jmeno": u.jmeno,
        "email": u.email,
        "role": u.role,
        "password": (
            password if not send_email else None
        ),  # Vrať heslo jen pokud se neposílá email
    }


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


@router.post("/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    send_email: bool = True,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reset hesla uživatele (pouze pro adminy)

    Args:
        user_id: ID uživatele
        send_email: Zda poslat email s novým heslem (výchozí True)

    Returns:
        Nové heslo (pokud send_email=False) nebo potvrzení o odeslání emailu
    """
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Vygeneruj nové náhodné heslo
    new_password = generate_random_password()

    # Aktualizuj heslo v databázi
    user.password_hash = hash_password(new_password)
    db.commit()

    # Odešli email s novým heslem
    if send_email:
        try:
            send_password_reset_email(
                to_email=user.email,
                user_name=user.jmeno,
                new_password=new_password,
                is_new_user=False,
            )
            return {
                "status": "ok",
                "message": f"Nové heslo bylo odesláno na email {user.email}",
            }
        except Exception as e:
            print(f"Chyba při odesílání emailu: {e}")
            return {
                "status": "error",
                "message": "Heslo bylo změněno, ale email se nepodařilo odeslat",
                "password": new_password,
            }
    else:
        return {
            "status": "ok",
            "message": "Heslo bylo změněno",
            "password": new_password,
        }
