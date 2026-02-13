from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date

from ..auth import get_db, get_current_user
from ..models import Neshoda, User, AuditExecution, LpaAssignment, Line, ChecklistCategory, AuditAnswer, ChecklistQuestion

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

    n.status = "taken_over"
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

    n.status = "known_solution"
    n.known_solution_at = datetime.utcnow()
    n.known_solution_by = current.id
    if note:
        n.poznamka = note

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

    n.status = "implemented"
    n.implemented_at = datetime.utcnow()
    n.implemented_by = current.id
    if note:
        n.poznamka = note

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
    neshoda.assigned_at = datetime.utcnow()

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
    poznamka: str = None,
    termin: date = None,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    neshoda = db.query(Neshoda).get(neshoda_id)

    if not neshoda:
        raise HTTPException(404, "Neshoda nenalezena")

    if current.id != neshoda.solver_id and current.role != "admin":
        raise HTTPException(403, "Nejsi přidělený řešitel")

    neshoda.status = "resolved"
    if poznamka:
        neshoda.poznamka = poznamka
    if termin:
        neshoda.termin = termin
    neshoda.resolved_at = datetime.utcnow()

    db.commit()
    return {"message": "Neshoda označena jako vyřešená"}

#================ Uzavření auditorem =============
@router.post("/{id}/close")
def close_issue(id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    issue = db.query(Neshoda).get(id)

    if not issue:
        raise HTTPException(404, "Neshoda nenalezena")

    # Jen auditor nebo admin může uzavřít
    if current.role not in ["auditor", "admin"]:
        raise HTTPException(403, "Nemáš oprávnění uzavřít neshodu")

    issue.status = "closed"
    issue.closed_at = datetime.utcnow()

    db.commit()
    return {"ok": True}


#================ Přiřazení řešitele + termín (auditor/admin) =============
from pydantic import BaseModel

class AssignSolverRequest(BaseModel):
    solver_id: int
    termin: Optional[date] = None
    poznamka: Optional[str] = None

@router.post("/{neshoda_id}/assign-solver")
def assign_solver_with_deadline(
    neshoda_id: int,
    data: AssignSolverRequest,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Auditor nebo admin může přiřadit řešitele a termín nápravy"""
    
    # Ověření oprávnění
    if current.role not in ["auditor", "admin"]:
        raise HTTPException(403, "Pouze auditor nebo admin může přiřadit řešitele")
    
    # Najdi neshodu
    neshoda = db.query(Neshoda).filter(Neshoda.id == neshoda_id).first()
    if not neshoda:
        raise HTTPException(404, "Neshoda nenalezena")
    
    # Ověř, že řešitel existuje a má správnou roli
    solver = db.query(User).filter(
        User.id == data.solver_id,
        User.role == "solver"
    ).first()
    
    if not solver:
        raise HTTPException(400, "Uživatel není řešitel nebo neexistuje")
    
    # Přiřaď řešitele a termín
    neshoda.solver_id = data.solver_id
    neshoda.termin = data.termin
    neshoda.status = "assigned"  # Změna stavu na přiřazeno
    
    if data.poznamka:
        neshoda.poznamka = data.poznamka
    
    db.commit()
    db.refresh(neshoda)
    
    return {
        "message": "Řešitel úspěšně přiřazen",
        "neshoda_id": neshoda.id,
        "solver_name": solver.jmeno,
        "termin": neshoda.termin,
    }


#================ Seznam řešitelů =============
@router.get("/solvers")
def get_solvers(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Vrátí seznam všech řešitelů pro dropdown"""
    
    solvers = db.query(User).filter(User.role == "solver").all()
    
    return [
        {
            "id": s.id,
            "jmeno": s.jmeno,
            "email": s.email,
        }
        for s in solvers
    ]


#================ Detail neshody s fotkou =============
@router.get("/{neshoda_id}/detail")
def get_neshoda_detail(
    neshoda_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Vrátí detail neshody včetně fotky z auditu"""
    
    neshoda = db.query(Neshoda).filter(Neshoda.id == neshoda_id).first()
    if not neshoda:
        raise HTTPException(404, "Neshoda nenalezena")
    
    # Najdi souvisící execution
    execution = db.query(AuditExecution).filter(
        AuditExecution.id == neshoda.audit_execution_id
    ).first()
    
    if not execution:
        raise HTTPException(404, "Audit execution nenalezen")
    
    # Najdi assignment pro kontext
    assignment = db.query(LpaAssignment).filter(
        LpaAssignment.id == execution.assignment_id
    ).first()
    
    # Najdi linku a kategorii
    line = db.query(Line).filter(Line.id == assignment.line_id).first() if assignment else None
    category = db.query(ChecklistCategory).filter(
        ChecklistCategory.id == assignment.category_id
    ).first() if assignment else None
    
    # Najdi NOK odpovědi s fotkami pro tento execution
    nok_answers = db.query(
        AuditAnswer,
        ChecklistQuestion.question_text
    ).join(
        ChecklistQuestion,
        AuditAnswer.question_id == ChecklistQuestion.id
    ).filter(
        AuditAnswer.audit_execution_id == neshoda.audit_execution_id,
        AuditAnswer.odpoved == "NOK"
    ).all()
    
    # Najdi řešitele, pokud je přiřazen
    solver = None
    if neshoda.solver_id:
        solver = db.query(User).filter(User.id == neshoda.solver_id).first()
    
    return {
        "id": neshoda.id,
        "popis": neshoda.popis,
        "poznamka": neshoda.poznamka,
        "zavaznost": neshoda.zavaznost,
        "status": neshoda.status,
        "termin": neshoda.termin,
        "solver": {
            "id": solver.id,
            "jmeno": solver.jmeno,
            "email": solver.email
        } if solver else None,
        "audit_info": {
            "execution_id": execution.id,
            "started_at": execution.started_at,
            "line_name": line.name if line else None,
            "category_name": category.name if category else None,
        },
        "nok_items": [
            {
                "question_text": question_text,
                "picture_url": answer.picture_url,
            }
            for answer, question_text in nok_answers
        ]
    }
