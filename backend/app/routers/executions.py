from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date
from typing import Optional

from ..auth import get_db, get_current_user
from ..models import (
    AuditExecution, 
    LpaAssignment, 
    User, 
    Line,
    ChecklistCategory,
    LpaCampaign,
    AuditAnswer,
)

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
        assignment.datum_provedeni = date.today()

    db.commit()

    return {"message": "Audit úspěšně ukončen"}

@router.get("/by-assignment/{assignment_id}")
def get_execution_by_assignment_path(
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


# ========== NOVÉ ENDPOINTY PRO PŘEHLED AUDITŮ ==========

@router.get("/list")
def list_audits(
    status: Optional[str] = None,
    line_id: Optional[int] = None,
    category_id: Optional[int] = None,
    auditor_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    result_filter: Optional[str] = Query(None, description="all, ok, nok"),
    month: Optional[str] = None,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Vrátí seznam všech auditů s filtry a statistikami
    """
    query = (
        db.query(
            AuditExecution,
            LpaAssignment,
            Line.name.label("line_name"),
            ChecklistCategory.name.label("category_name"),
            LpaCampaign.month,
            User.jmeno.label("auditor_name"),
        )
        .join(LpaAssignment, AuditExecution.assignment_id == LpaAssignment.id)
        .join(Line, LpaAssignment.line_id == Line.id)
        .join(ChecklistCategory, LpaAssignment.category_id == ChecklistCategory.id)
        .join(LpaCampaign, LpaAssignment.campaign_id == LpaCampaign.id)
        .join(User, AuditExecution.auditor_id == User.id)
    )

    # Filtry
    if status:
        query = query.filter(AuditExecution.status == status)
    
    if line_id:
        query = query.filter(LpaAssignment.line_id == line_id)
    
    if category_id:
        query = query.filter(LpaAssignment.category_id == category_id)
    
    if auditor_id:
        query = query.filter(AuditExecution.auditor_id == auditor_id)
    
    if date_from:
        query = query.filter(AuditExecution.started_at >= date_from)
    
    if date_to:
        query = query.filter(AuditExecution.started_at <= date_to)
    
    if month:
        query = query.filter(LpaCampaign.month == month)

    results = query.order_by(AuditExecution.started_at.desc()).all()

    # Zpracuj výsledky a přidej statistiky
    audits_list = []
    
    for execution, assignment, line_name, category_name, campaign_month, auditor_name in results:
        # Spočítej OK/NOK pro tento audit
        answers = (
            db.query(AuditAnswer)
            .filter(AuditAnswer.audit_execution_id == execution.id)
            .all()
        )
        
        total = len(answers)
        ok_count = sum(1 for a in answers if a.odpoved == "OK")
        nok_count = sum(1 for a in answers if a.odpoved == "NOK")
        ok_percent = round((ok_count / total) * 100, 1) if total > 0 else 0
        
        # Filtr podle výsledku
        if result_filter == "ok" and nok_count > 0:
            continue
        if result_filter == "nok" and nok_count == 0:
            continue
        
        audits_list.append({
            "execution_id": execution.id,
            "assignment_id": assignment.id,
            "status": execution.status,
            "started_at": execution.started_at,
            "finished_at": execution.finished_at,
            "line_name": line_name,
            "category_name": category_name,
            "month": campaign_month,
            "auditor_name": auditor_name,
            "auditor_id": execution.auditor_id,
            "stats": {
                "total": total,
                "ok": ok_count,
                "nok": nok_count,
                "ok_percent": ok_percent,
            }
        })

    return audits_list


@router.get("/stats/summary")
def get_overall_stats(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Vrátí celkové statistiky auditů
    """
    query = db.query(AuditExecution)
    
    if date_from:
        query = query.filter(AuditExecution.started_at >= date_from)
    if date_to:
        query = query.filter(AuditExecution.started_at <= date_to)
    
    executions = query.all()
    execution_ids = [e.id for e in executions]
    
    if not execution_ids:
        return {
            "total_audits": 0,
            "completed_audits": 0,
            "in_progress_audits": 0,
            "total_questions": 0,
            "ok_answers": 0,
            "nok_answers": 0,
            "ok_percent": 0,
        }
    
    answers = (
        db.query(AuditAnswer)
        .filter(AuditAnswer.audit_execution_id.in_(execution_ids))
        .all()
    )
    
    total_audits = len(executions)
    completed = sum(1 for e in executions if e.status == "done")
    in_progress = sum(1 for e in executions if e.status == "in_progress")
    
    total_questions = len(answers)
    ok_count = sum(1 for a in answers if a.odpoved == "OK")
    nok_count = sum(1 for a in answers if a.odpoved == "NOK")
    ok_percent = round((ok_count / total_questions) * 100, 1) if total_questions > 0 else 0
    
    return {
        "total_audits": total_audits,
        "completed_audits": completed,
        "in_progress_audits": in_progress,
        "total_questions": total_questions,
        "ok_answers": ok_count,
        "nok_answers": nok_count,
        "ok_percent": ok_percent,
    }
