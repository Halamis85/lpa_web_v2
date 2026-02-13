from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
import random

from ..auth import get_db, get_current_user
from ..models import User, LpaCampaign, LpaAssignment, Line, ChecklistTemplate, ChecklistCategory 

router = APIRouter()

@router.post("/")
def create_campaign(
    month: str,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    existing = db.query(LpaCampaign).filter_by(month=month).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Kampaň pro tento měsíc už existuje"
        )

    campaign = LpaCampaign(
        month=month,
        created_by=current.id,
        status="draft",
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign

@router.get("/")
def list_campaigns(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(LpaCampaign).all()

@router.get("/{campaign_id}")
def get_campaign(
    campaign_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    campaign = db.query(LpaCampaign).filter_by(id=campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Kampaň nenalezena")

    return campaign

@router.post("/{month}/generate-assignments")
def generate_assignments(
    month: str,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    # 1) Najdeme kampaň
    campaign = db.query(LpaCampaign).filter_by(month=month).first()
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Kampaň pro tento měsíc neexistuje"
        )

    # 2) Auditoři
    auditors = db.query(User).filter_by(role="auditor").all()
    if not auditors:
        raise HTTPException(
            status_code=400,
            detail="Neexistují žádní auditoři"
        )

    # 3) Linky
    lines = db.query(Line).all()
    if not lines:
        raise HTTPException(
            status_code=400,
            detail="Neexistují žádné linky"
        )

    # 4) Kategorie checklistu (OBLASTI)
    categories = db.query(ChecklistCategory).all()
    if not categories:
        raise HTTPException(
            status_code=400,
            detail="Neexistují žádné checklist kategorie"
        )

    # 5) Zabránit dvojímu generování
    existing = (
        db.query(LpaAssignment)
        .filter(LpaAssignment.campaign_id == campaign.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Přidělení pro tuto kampaň už byla vygenerována"
        )

    assignments = []
    auditor_index = 0
    category_index = 0

    for line in lines:
        auditor = auditors[auditor_index % len(auditors)]
        auditor_index += 1

        category = categories[category_index % len(categories)]
        category_index += 1

        # Najdeme checklist šablonu pro linku
        template = (
            db.query(ChecklistTemplate)
            .filter(ChecklistTemplate.line_id == line.id)
            .first()
        )

        if not template:
            raise HTTPException(
                status_code=400,
                detail=f"Neexistuje checklist šablona pro linku {line.name}"
            )

        assignment = LpaAssignment(
            campaign_id=campaign.id,
            auditor_id=auditor.id,
            line_id=line.id,
            template_id=template.id,
            category_id=category.id,   # 🔹 KLÍČOVÉ
            termin=f"{month}-28",
            status="pending",
        )

        db.add(assignment)
        assignments.append({
            "line": line.name,
            "auditor": auditor.jmeno,
            "category": category.name,
        })

    campaign.status = "generated"
    db.commit()

    return {
        "message": "Assignments generated",
        "assignments": assignments,
    }
#-- náhodné 7 až 20 dná od prvního generování
def random_deadline_from(today: date) -> date:
    return today + timedelta(days=random.randint(7, 20))

@router.post("/auto-generate-current")
def auto_generate_current_month(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Jen admin")

    today = date.today()
    month = today.strftime("%Y-%m")

    # === 1) Najdeme nebo vytvoříme kampaň ===
    campaign = (
        db.query(LpaCampaign)
        .filter(LpaCampaign.month == month)
        .first()
    )

    if not campaign:
        campaign = LpaCampaign(
            month=month,
            created_by=current.id,
            status="draft",
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

    # === 2) Pokud už přidělení existují → stop ===
    existing = (
        db.query(LpaAssignment)
        .filter(LpaAssignment.campaign_id == campaign.id)
        .first()
    )

    if existing:
        return {
            "message": f"Přidělení pro {month} už existují — nic nebylo změněno."
        }

    # === 3) Načteme auditory, linky a kategorie ===
    auditors = db.query(User).filter(User.role == "auditor").all()
    if not auditors:
        raise HTTPException(400, "Neexistují žádní auditoři")

    lines = db.query(Line).all()
    if not lines:
        raise HTTPException(400, "Neexistují žádné linky")

    categories = db.query(ChecklistCategory).all()
    if not categories:
        raise HTTPException(400, "Neexistují žádné checklist kategorie")

    assignments_count = 0
    auditor_index = 0
    category_index = 0

    for line in lines:
        auditor = auditors[auditor_index % len(auditors)]
        auditor_index += 1

        category = categories[category_index % len(categories)]
        category_index += 1

        template = (
            db.query(ChecklistTemplate)
            .filter(ChecklistTemplate.line_id == line.id)
            .first()
        )

        if not template:
            raise HTTPException(
                400,
                f"Neexistuje checklist šablona pro linku {line.name}",
            )

        assignment = LpaAssignment(
            campaign_id=campaign.id,
            auditor_id=auditor.id,
            line_id=line.id,
            category_id=category.id,   # ✅ TEĎ UŽ JE DEFINOVANÁ
            template_id=template.id,
            termin=random_deadline_from(today),
            status="pending",          # ✅ NOVÉ PŘIDĚLENÍ = pending
        )

        db.add(assignment)
        assignments_count += 1

    campaign.status = "generated"
    db.commit()

    return {
        "message": f"Vygenerováno {assignments_count} přidělení pro {month}",
        "assignments_count": assignments_count,
    }
