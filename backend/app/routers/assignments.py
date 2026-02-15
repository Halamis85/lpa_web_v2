from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, timedelta

from ..auth import get_db, get_current_user
from ..models import (
    User,
    LpaCampaign,
    LpaAssignment,
    Line,
    ChecklistTemplate,
    ChecklistCategory,
    AuditExecution,
    AuditAnswer,
    ChecklistQuestion,
)

router = APIRouter()


@router.post("/")
def create_assignment(
    campaign_id: int,
    auditor_id: int,
    line_id: int,
    termin: str,  # YYYY-MM-DD
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    # Kontrola kampaně
    campaign = db.query(LpaCampaign).filter(LpaCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Kampaň nenalezena")

    # Kontrola auditora
    auditor = db.query(User).filter(User.id == auditor_id).first()
    if not auditor or auditor.role != "auditor":
        raise HTTPException(status_code=400, detail="Neplatný auditor")

    # Kontrola linky
    line = db.query(Line).filter(Line.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="Linka nenalezena")

    try:
        termin_date = date.fromisoformat(termin)
    except ValueError:
        raise HTTPException(status_code=400, detail="Termin musí být YYYY-MM-DD")

    # Najdeme checklist šablonu pro linku
    template = (
        db.query(ChecklistTemplate).filter(ChecklistTemplate.line_id == line_id).first()
    )

    if not template:
        raise HTTPException(
            status_code=400,
            detail=f"Neexistuje checklist šablona pro linku {line.name}",
        )

    assignment = LpaAssignment(
        campaign_id=campaign_id,
        auditor_id=auditor_id,
        line_id=line_id,
        template_id=template.id,
        termin=termin_date,
        status="pending",
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("")
def list_assignments(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = (
        db.query(
            LpaAssignment.id,
            LpaAssignment.status,
            LpaAssignment.termin,
            LpaCampaign.month,
            Line.name.label("line_name"),
            ChecklistCategory.name.label("category_name"),
            LpaAssignment.auditor_id,
        )
        .join(LpaCampaign, LpaAssignment.campaign_id == LpaCampaign.id)
        .join(Line, LpaAssignment.line_id == Line.id)
        .join(ChecklistCategory, LpaAssignment.category_id == ChecklistCategory.id)
    )

    # Auditor vidí jen svá přidělení
    if current.role == "auditor":
        q = q.filter(LpaAssignment.auditor_id == current.id)

    results = q.all()

    return [
        {
            "id": r.id,
            "status": r.status,
            "termin": r.termin.isoformat() if r.termin else None,
            "month": r.month,
            "line_name": r.line_name,
            "category_name": r.category_name,
        }
        for r in results
    ]


@router.get("/{assignment_id}")
def get_assignment(
    assignment_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assignment = (
        db.query(LpaAssignment).filter(LpaAssignment.id == assignment_id).first()
    )

    if not assignment:
        raise HTTPException(status_code=404, detail="Přidělení nenalezeno")

    if current.role == "auditor" and assignment.auditor_id != current.id:
        raise HTTPException(status_code=403, detail="Toto přidělení není tvoje")

    return assignment


@router.post("/{month}/generate-assignments")
def generate_assignments(
    month: str,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    campaign = db.query(LpaCampaign).filter_by(month=month).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Kampaň pro tento měsíc neexistuje")

    auditors = db.query(User).filter_by(role="auditor").all()
    if not auditors:
        raise HTTPException(status_code=400, detail="Neexistují žádní auditoři")

    lines = db.query(Line).all()
    if not lines:
        raise HTTPException(status_code=400, detail="Neexistují žádné linky")

    existing = (
        db.query(LpaAssignment).filter(LpaAssignment.campaign_id == campaign.id).first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Přidělení pro tuto kampaň už byla vygenerována"
        )

    assignments = []
    auditor_index = 0

    for line in lines:
        auditor = auditors[auditor_index % len(auditors)]
        auditor_index += 1

        template = (
            db.query(ChecklistTemplate)
            .filter(ChecklistTemplate.line_id == line.id)
            .first()
        )

        if not template:
            raise HTTPException(
                status_code=400,
                detail=f"Neexistuje checklist šablona pro linku {line.name}",
            )

        assignment = LpaAssignment(
            campaign_id=campaign.id,
            auditor_id=auditor.id,
            line_id=line.id,
            template_id=template.id,
            termin=date.fromisoformat(f"{month}-28"),
            status="pending",
        )

        db.add(assignment)
        assignments.append(
            {
                "line": line.name,
                "auditor": auditor.jmeno,
                "template_id": template.id,
            }
        )

    campaign.status = "generated"
    db.commit()

    return {
        "message": "Assignments generated",
        "assignments": assignments,
    }


@router.get("/{assignment_id}/report")
def get_assignment_report(
    assignment_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1) Najdeme assignment + navázané věci přes JOIN
    assignment_data = (
        db.query(
            LpaAssignment,
            LpaCampaign.month.label("campaign_month"),
            Line.name.label("line_name"),
            ChecklistCategory.name.label("category_name"),
        )
        .join(LpaCampaign, LpaAssignment.campaign_id == LpaCampaign.id)
        .join(Line, LpaAssignment.line_id == Line.id)
        .join(ChecklistCategory, LpaAssignment.category_id == ChecklistCategory.id)
        .filter(LpaAssignment.id == assignment_id)
        .first()
    )

    if not assignment_data:
        raise HTTPException(status_code=404, detail="Přidělení nenalezeno")

    assignment, month, line_name, category_name = assignment_data

    # 2) Bezpečnost: auditor jen své
    if current.role == "auditor" and assignment.auditor_id != current.id:
        raise HTTPException(status_code=403, detail="Toto není tvůj audit")

    # 3) Najdeme poslední execution pro tento assignment
    execution = (
        db.query(AuditExecution)
        .filter(AuditExecution.assignment_id == assignment_id)
        .order_by(AuditExecution.started_at.desc())
        .first()
    )

    if not execution:
        raise HTTPException(
            status_code=400, detail="Pro tento assignment zatím neexistuje žádný audit"
        )

    # 4) Načteme otázky + odpovědi
    answers = (
        db.query(
            ChecklistQuestion.id.label("question_id"),
            ChecklistQuestion.question_text,
            ChecklistQuestion.position,
            ChecklistCategory.name.label("category_name"),
            AuditAnswer.odpoved,
            AuditAnswer.picture_url,
        )
        .join(ChecklistQuestion, ChecklistQuestion.id == AuditAnswer.question_id)
        .join(ChecklistCategory, ChecklistCategory.id == ChecklistQuestion.category_id)
        .filter(AuditAnswer.audit_execution_id == execution.id)
        .order_by(ChecklistQuestion.position)
        .all()
    )

    return {
        "assignment": {
            "id": assignment.id,
            "status": assignment.status,
            "termin": assignment.termin,
            "datum_provedeni": assignment.datum_provedeni,
        },
        "campaign_month": month,
        "line": line_name,
        "category": category_name,
        "answers": [
            {
                "question_id": a.question_id,
                "question_text": a.question_text,
                "position": a.position,
                "category": a.category_name,
                "odpoved": a.odpoved,
                "picture_url": a.picture_url,
            }
            for a in answers
        ],
    }


@router.post("/{assignment_id}/set-status")
def set_assignment_status(
    assignment_id: int,
    status: str,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(403, "Jen admin může měnit stav")

    assignment = db.query(LpaAssignment).get(assignment_id)
    if not assignment:
        raise HTTPException(404, "Přidělení nenalezeno")

    if status not in ["pending", "in_progress", "done"]:
        raise HTTPException(400, "Neplatný stav")

    assignment.status = status

    if status == "done":
        assignment.datum_provedeni = date.today()
    elif status == "in_progress":
        assignment.datum_provedeni = None

    db.commit()

    return {"message": f"Stav změněn na {status}"}


@router.get("/allocations")
def list_allocations(
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = (
        db.query(
            User.jmeno.label("auditor"),
            Line.name.label("line"),
            ChecklistCategory.name.label("category"),
            LpaCampaign.month,
            LpaAssignment.termin,
            LpaAssignment.status,
        )
        .join(User, LpaAssignment.auditor_id == User.id)
        .join(Line, LpaAssignment.line_id == Line.id)
        .join(ChecklistCategory, LpaAssignment.category_id == ChecklistCategory.id)
        .join(LpaCampaign, LpaAssignment.campaign_id == LpaCampaign.id)
        .all()
    )

    return [
        {
            "auditor": r.auditor,
            "line": r.line,
            "category": r.category,
            "month": r.month,
            "termin": r.termin,
            "status": r.status,
        }
        for r in results
    ]


@router.get("/allocations/by-month/{month}")
def get_allocations_by_month(
    month: str,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Vrátí detailní přehled všech přidělení pro daný měsíc se stavem splnitelnosti"""
    from datetime import date

    # Kontrola práv - pouze admin a auditor
    if current.role not in ["admin", "auditor"]:
        raise HTTPException(403, "Nemáte oprávnění k zobrazení rozlosování")

    results = (
        db.query(
            LpaAssignment.id.label("assignment_id"),
            User.jmeno.label("auditor_name"),
            User.id.label("auditor_id"),
            Line.name.label("line_name"),
            ChecklistCategory.name.label("category_name"),
            LpaCampaign.month,
            LpaAssignment.termin,
            LpaAssignment.status,
            LpaAssignment.datum_provedeni,
            AuditExecution.id.label("execution_id"),
            AuditExecution.finished_at,
        )
        .join(User, LpaAssignment.auditor_id == User.id)
        .join(Line, LpaAssignment.line_id == Line.id)
        .join(ChecklistCategory, LpaAssignment.category_id == ChecklistCategory.id)
        .join(LpaCampaign, LpaAssignment.campaign_id == LpaCampaign.id)
        .outerjoin(AuditExecution, LpaAssignment.id == AuditExecution.assignment_id)
        .filter(LpaCampaign.month == month)
        .order_by(User.jmeno, Line.name)
        .all()
    )

    today = date.today()
    allocations_list = []

    for r in results:
        # Určení stavu splnitelnosti
        completion_status = "pending"  # výchozí
        is_overdue = False

        if r.status == "done":
            completion_status = "completed"
        elif r.status == "in_progress":
            completion_status = "in_progress"
        elif r.termin and r.termin < today:
            completion_status = "overdue"
            is_overdue = True

        allocations_list.append(
            {
                "assignment_id": r.assignment_id,
                "auditor_name": r.auditor_name,
                "auditor_id": r.auditor_id,
                "line_name": r.line_name,
                "category_name": r.category_name,
                "month": r.month,
                "termin": r.termin.isoformat() if r.termin else None,
                "status": r.status,
                "completion_status": completion_status,
                "is_overdue": is_overdue,
                "datum_provedeni": (
                    r.datum_provedeni.isoformat() if r.datum_provedeni else None
                ),
                "execution_id": r.execution_id,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            }
        )

    # Pokud je uživatel auditor, zobraz pouze jeho přidělení
    if current.role == "auditor":
        allocations_list = [
            a for a in allocations_list if a["auditor_id"] == current.id
        ]

    # Statistiky
    total = len(allocations_list)
    completed = len(
        [a for a in allocations_list if a["completion_status"] == "completed"]
    )
    in_progress = len(
        [a for a in allocations_list if a["completion_status"] == "in_progress"]
    )
    overdue = len([a for a in allocations_list if a["is_overdue"]])
    pending = total - completed - in_progress - overdue

    return {
        "allocations": allocations_list,
        "stats": {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "overdue": overdue,
            "completion_rate": round((completed / total * 100), 1) if total > 0 else 0,
        },
    }
