from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..auth import get_db, get_current_user
from ..models import AuditExecution, LpaAssignment, User

router = APIRouter()

@router.post("/start")
def start_audit(
    assignment_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1) Najdi přidělení
    assignment = db.query(LpaAssignment).filter(
        LpaAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Přidělení nenalezeno")

    # 2) Ověř oprávnění
    if current.role == "auditor" and assignment.auditor_id != current.id:
        raise HTTPException(
            status_code=403,
            detail="Toto přidělení nepatří tomuto auditorovi"
        )

    if current.role not in ["auditor", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Jen auditor nebo admin může zahájit audit"
        )

    # 3) Ověř stav přidělení
    if assignment.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Audit nelze spustit, aktuální stav: {assignment.status}"
        )

    # 4) Vytvoř execution záznam
    execution = AuditExecution(
        assignment_id=assignment_id,
        auditor_id=current.id,
        started_at=datetime.utcnow(),
        status="in_progress",
    )

    # 5) Aktualizuj stav přidělení
    assignment.status = "in_progress"

    db.add(execution)
    db.commit()
    db.refresh(execution)

    return {
        "execution_id": execution.id,
        "assignment_id": assignment.id,
        "status": execution.status,
        "started_at": execution.started_at,
    }

@router.get("/by-assignment")
def get_execution_by_assignment(
    assignment_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    execution = (
        db.query(AuditExecution)
        .filter(AuditExecution.assignment_id == assignment_id)
        .first()
    )

    if not execution:
        raise HTTPException(status_code=404, detail="Audit ještě nebyl zahájen")

    return {"execution_id": execution.id}


@router.post("/finish")
def finish_audit(
    execution_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    execution = (
        db.query(AuditExecution)
        .filter(AuditExecution.id == execution_id)
        .first()
    )

    if not execution:
        raise HTTPException(status_code=404, detail="Audit nenalezen")

    if current.role == "auditor" and execution.auditor_id != current.id:
        raise HTTPException(status_code=403, detail="Toto není tvůj audit")

    # Uzavřeme audit
    execution.status = "done"
    execution.finished_at = datetime.utcnow()

    # Uzavřeme i přidělení
    assignment = (
        db.query(LpaAssignment)
        .filter(LpaAssignment.id == execution.assignment_id)
        .first()
    )

    if assignment:
        assignment.status = "done"

    db.commit()

    return {"message": "Audit úspěšně ukončen"}

@router.get("/by-assignment/{assignment_id}")
def get_execution_by_assignment(
    assignment_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    execution = (
        db.query(AuditExecution)
        .filter(AuditExecution.assignment_id == assignment_id)
        .first()
    )

    if not execution:
        raise HTTPException(404, "Execution neexistuje")

    return {"execution_id": execution.id}

@router.get("/{execution_id}")
def get_execution(
    execution_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    execution = db.query(AuditExecution).filter_by(id=execution_id).first()

    if not execution:
        raise HTTPException(404, "Execution nenalezen")

    return {
        "execution_id": execution.id,
        "assignment_id": execution.assignment_id
    }
