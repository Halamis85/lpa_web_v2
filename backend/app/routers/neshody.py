from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..auth import get_db, get_current_user
from ..models import Neshoda, User, AuditExecution, LpaAssignment, Line, ChecklistCategory, AuditAnswer, date

router = APIRouter()


# ======== SEZNAM NESHOD ========

@router.get("/")
def list_neshody(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = (
        db.query(Neshoda, AuditExecution, LpaAssignment, Line, ChecklistCategory)
        .join(AuditExecution, Neshoda.audit_execution_id == AuditExecution.id)
        .join(LpaAssignment, AuditExecution.assignment_id == LpaAssignment.id)
        .join(Line, LpaAssignment.line_id == Line.id)
        .join(ChecklistCategory, LpaAssignment.category_id == ChecklistCategory.id)
    )

    results = q.all()

    return [
        {
            "id": n.id,
            "status": n.status,
            "zavaznost": n.zavaznost,
            "popis": n.popis,
            "poznamka": n.poznamka,
            "solver_id": n.solver_id,
            "termin": n.termin,
            "line_name": line.name,
            "category_name": cat.name,
            "picture_url": ans.picture_url if (ans := db.query(AuditAnswer)
            .filter(AuditAnswer.audit_execution_id == n.audit_execution_id)
            .first()) else None,
        }
        for n, exec, assign, line, cat in results
    ]

# ======== PŘEVZETÍ NESHODY ========

@router.post("/{neshoda_id}/take-over")
def take_over_neshoda(
    neshoda_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    n = db.query(Neshoda).filter(Neshoda.id == neshoda_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Neshoda nenalezena")

    # Jen solver nebo admin může převzít
    if current.role not in ["solver", "admin"]:
        raise HTTPException(status_code=403, detail="Jen řešitel může převzít neshodu")

    n.stav = "taken_over"
    n.taken_over_at = datetime.utcnow()
    n.taken_over_by = current.id
    n.solver_id = current.id  # přiřadíme řešitele

    db.commit()
    db.refresh(n)
    return n


# ======== ZNÁMÉ ŘEŠENÍ ========

@router.post("/{neshoda_id}/known-solution")
def set_known_solution(
    neshoda_id: int,
    note: str | None = None,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    n = db.query(Neshoda).filter(Neshoda.id == neshoda_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Neshoda nenalezena")

    if current.role not in ["solver", "admin"]:
        raise HTTPException(status_code=403, detail="Jen řešitel může zadat známé řešení")

    n.stav = "known_solution"
    n.known_solution_at = datetime.utcnow()
    n.known_solution_by = current.id
    if note:
        n.note = note

    db.commit()
    db.refresh(n)
    return n


# ======== IMPLEMENTACE ŘEŠENÍ ========

@router.post("/{neshoda_id}/implement")
def implement_solution(
    neshoda_id: int,
    note: str | None = None,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    n = db.query(Neshoda).filter(Neshoda.id == neshoda_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Neshoda nenalezena")

    if current.role not in ["solver", "admin"]:
        raise HTTPException(status_code=403, detail="Jen řešitel může implementovat řešení")

    n.stav = "implemented"
    n.implemented_at = datetime.utcnow()
    n.implemented_by = current.id
    if note:
        n.note = note

    db.commit()
    db.refresh(n)
    return n


# ======== UZAVŘENÍ NESHODY ========

@router.post("/{neshoda_id}/close")
def close_neshoda(
    neshoda_id: int,
    note: str | None = None,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    n = db.query(Neshoda).filter(Neshoda.id == neshoda_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Neshoda nenalezena")

    # Uzavírat může auditor (kontrolor) nebo admin
    if current.role not in ["auditor", "admin"]:
        raise HTTPException(status_code=403, detail="Jen auditor nebo admin může uzavřít neshodu")

    n.stav = "closed"
    n.closed_at = datetime.utcnow()
    n.closed_by = current.id
    if note:
        n.note = note

    db.commit()
    db.refresh(n)
    return n

# ======== přidělit řešitele ========
@router.post("/{neshoda_id}/assign")
def assign_solver(
    neshoda_id: int,
    solver_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role not in ["admin", "solver"]:
        raise HTTPException(403, "Nemáš oprávnění")

    neshoda = db.query(Neshoda).get(neshoda_id)
    if not neshoda:
        raise HTTPException(404, "Neshoda nenalezena")

    solver = db.query(User).filter(User.id == solver_id, User.role == "solver").first()
    if not solver:
        raise HTTPException(400, "Neplatný řešitel")

    neshoda.solver_id = solver_id
    neshoda.status = "in_progress"
    neshoda.prevzato_at = datetime.utcnow()

    db.commit()
    return {"message": "Řešitel přidělen"}

# ======== převzetí řešitele ========
@router.post("/{id}/take")
def take_issue(id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    issue = db.query(Neshoda).get(id)

    if not issue:
        raise HTTPException(404, "Neshoda neexistuje")

    issue.status = "in_progress"
    issue.started_at = datetime.utcnow()
    issue.solver_id = current.id

    db.commit()
    return {"ok": True}

# ======== označit vyřešené ========

@router.post("/{neshoda_id}/resolve")
def resolve_neshoda(
    neshoda_id: int,
    poznamka: str,
    termin: date,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    neshoda = db.query(Neshoda).get(neshoda_id)

    if not neshoda:
        raise HTTPException(404, "Neshoda nenalezena")

    if current.id != neshoda.solver_id and current.role != "admin":
        raise HTTPException(403, "Nejsi přidělený řešitel")

    neshoda.status = "resolved"
    neshoda.poznamka = poznamka
    neshoda.termin = termin
    neshoda.zname_reseni_at = datetime.utcnow()

    db.commit()
    return {"message": "Neshoda označena jako vyřešená"}
#========== Označení opraveno =============
@router.post("/{id}/resolve")
def resolve_issue(id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    issue = db.query(Neshoda).get(id)

    issue.status = "resolved"
    issue.resolved_at = datetime.utcnow()

    db.commit()
    return {"ok": True}
#================ Uzavření auditorem =============
@router.post("/{id}/close")
def close_issue(id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    issue = db.query(Neshoda).get(id)

    issue.status = "closed"
    issue.closed_at = datetime.utcnow()

    db.commit()
    return {"ok": True}

# ======== finalní zavření  ========
@router.post("/{neshoda_id}/close")
def close_neshoda(
    neshoda_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    neshoda = db.query(Neshoda).get(neshoda_id)

    if not neshoda:
        raise HTTPException(404, "Neshoda nenalezena")

    if current.role != "admin":
        raise HTTPException(403, "Jen admin může uzavírat")

    neshoda.status = "closed"
    neshoda.uzavreno_at = datetime.utcnow()

    db.commit()
    return {"message": "Neshoda uzavřena"}

