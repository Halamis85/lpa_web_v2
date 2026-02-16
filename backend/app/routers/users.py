from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import secrets
import string

from ..auth import get_db, hash_password, get_current_user
from ..models import User
from ..email_service import send_password_reset_email

router = APIRouter()


def generate_random_password(length: int = 12) -> str:
    """Vygeneruje náhodné heslo"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password


# ===========================
# PYDANTIC SCHEMAS
# ===========================
class UserCreate(BaseModel):
    jmeno: str
    email: str
    roles: list[str]  # ["auditor", "solver"]
    send_email: bool = True


class UserUpdate(BaseModel):
    jmeno: str = None
    email: str = None
    roles: list[str] = None


# ===========================
# CRUD ENDPOINTY
# ===========================


@router.post("/create-first-admin")
def create_first_admin(db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == "admin@lpa.local").first()
    if existing:
        return {"status": "exists", "message": "Admin už existuje"}

    admin = User(
        jmeno="Admin",
        email="admin@lpa.local",
        role="admin",
        roles="admin",
        password_hash=hash_password("admin"),
        force_password_change=False,  # Admin nemusí měnit heslo
    )
    db.add(admin)
    db.commit()
    return {"status": "created", "message": "Admin vytvořen (heslo = admin)"}


@router.get("")
def list_users(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_inactive: bool = False,
):
    """Vrátí seznam všech uživatelů (pouze pro adminy)"""
    if not current.has_role("admin"):
        raise HTTPException(status_code=403, detail="Only admin")

    query = db.query(User)

    # Filtrovat neaktivní pokud není požadováno jinak
    if not include_inactive:
        query = query.filter(User.is_active == True)

    users = query.all()
    return [
        {
            "id": u.id,
            "jmeno": u.jmeno,
            "email": u.email,
            "role": u.role,
            "roles": u.get_roles_list(),
            "force_password_change": u.force_password_change,
            "is_active": u.is_active,
        }
        for u in users
    ]


@router.post("")
def create_user(
    user_data: UserCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Vytvoří nového uživatele s více rolemi a odešle mu email s přístupovými údaji

    Args:
        user_data: Data nového uživatele
            - jmeno: Jméno uživatele
            - email: Email uživatele
            - roles: Seznam rolí ["auditor", "solver", "admin"]
            - send_email: Zda poslat email s heslem (výchozí True)
    """
    if not current.has_role("admin"):
        raise HTTPException(status_code=403, detail="Only admin")

    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Validace rolí
    valid_roles = {"auditor", "solver", "admin"}
    if not all(r in valid_roles for r in user_data.roles):
        raise HTTPException(status_code=400, detail="Invalid role")

    # Hlavní role je první v seznamu
    primary_role = user_data.roles[0] if user_data.roles else "auditor"
    roles_str = ",".join(user_data.roles)

    # Vygeneruj náhodné heslo
    password = generate_random_password()

    u = User(
        jmeno=user_data.jmeno,
        email=user_data.email,
        role=primary_role,
        roles=roles_str,
        password_hash=hash_password(password),
        force_password_change=True,  # Nový uživatel musí změnit heslo
    )
    db.add(u)
    db.commit()
    db.refresh(u)

    if user_data.send_email:
        try:
            send_password_reset_email(
                to_email=user_data.email,
                user_name=user_data.jmeno,
                new_password=password,
                is_new_user=True,
            )
        except Exception as e:
            print(f"Chyba při odesílání emailu: {e}")

    return {
        "id": u.id,
        "jmeno": u.jmeno,
        "email": u.email,
        "role": u.role,
        "roles": u.get_roles_list(),
        "password": password if not user_data.send_email else None,
    }


@router.put("/{user_id}")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upraví existujícího uživatele (pouze pro adminy)

    Args:
        user_id: ID uživatele
        user_data: Nová data (jméno, email, role)
    """
    if not current.has_role("admin"):
        raise HTTPException(status_code=403, detail="Only admin")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Aktualizuj pole, pokud jsou zadána
    if user_data.jmeno is not None:
        user.jmeno = user_data.jmeno

    if user_data.email is not None:
        # Zkontroluj, zda email již není použit
        existing = (
            db.query(User)
            .filter(User.email == user_data.email, User.id != user_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = user_data.email

    if user_data.roles is not None:
        # Validace rolí
        valid_roles = {"auditor", "solver", "admin"}
        if not all(r in valid_roles for r in user_data.roles):
            raise HTTPException(status_code=400, detail="Invalid role")

        primary_role = user_data.roles[0] if user_data.roles else user.role
        user.role = primary_role
        user.roles = ",".join(user_data.roles)

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "jmeno": user.jmeno,
        "email": user.email,
        "role": user.role,
        "roles": user.get_roles_list(),
    }


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deaktivuje uživatele (soft delete)
    Uživatel nebude moct se přihlásit, ale data zůstávají zachovaná

    Args:
        user_id: ID uživatele k deaktivaci
    """
    if not current.has_role("admin"):
        raise HTTPException(status_code=403, detail="Only admin")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Nemůžeme deaktivovat sami sebe
    if user.id == current.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    # Deaktivace místo mazání
    user.is_active = False
    db.commit()

    return {"status": "ok", "message": f"Uživatel {user.jmeno} byl deaktivován"}


@router.patch("/{user_id}/roles")
def update_user_roles(
    user_id: int,
    roles: list[str],
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Aktualizuje role uživatele (pouze pro adminy)

    Args:
        user_id: ID uživatele
        roles: Seznam rolí ["auditor", "solver"]
    """
    if not current.has_role("admin"):
        raise HTTPException(status_code=403, detail="Only admin")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validace rolí
    valid_roles = {"auditor", "solver", "admin"}
    if not all(r in valid_roles for r in roles):
        raise HTTPException(status_code=400, detail="Invalid role")

    primary_role = roles[0] if roles else "auditor"
    user.role = primary_role
    user.roles = ",".join(roles)

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "jmeno": user.jmeno,
        "role": user.role,
        "roles": user.get_roles_list(),
    }


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
    """
    if not current.has_role("admin"):
        raise HTTPException(status_code=403, detail="Only admin")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Vygeneruj nové náhodné heslo
    new_password = generate_random_password()

    # Aktualizuj heslo a vyžaduj změnu při příštím přihlášení
    user.password_hash = hash_password(new_password)
    user.force_password_change = True
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


@router.post("/init-passwords")
def init_passwords(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Inicializuj hesla pro všechny uživatele (pouze pro adminy)"""
    if not current.has_role("admin"):
        raise HTTPException(status_code=403, detail="Only admin")

    users = db.query(User).all()
    for u in users:
        if u.email and not u.password_hash:
            u.password_hash = hash_password(u.email)
            u.force_password_change = True

    db.commit()
    return {"status": "ok", "message": "Hesla inicializována (dočasně = email)."}


@router.post("/{user_id}/activate")
def activate_user(
    user_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reaktivuje deaktivovaného uživatele
    Uživatel se opět může přihlásit do systému

    Args:
        user_id: ID uživatele k aktivaci
    """
    if not current.has_role("admin"):
        raise HTTPException(status_code=403, detail="Only admin")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()

    return {"status": "ok", "message": f"Uživatel {user.jmeno} byl aktivován"}
