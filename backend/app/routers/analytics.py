from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from ..auth import get_db, get_current_user
from ..models import AuditExecution, AuditAnswer, ChecklistCategory, Neshoda

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
def get_dashboard_data(
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Celková data za aktuální měsíc
    today = date.today()
    month_start = date(today.year, today.month, 1)

    executions = (
        db.query(AuditExecution)
        .filter(AuditExecution.started_at >= month_start)
        .all()
    )

    execution_ids = [e.id for e in executions]

    answers = (
        db.query(AuditAnswer)
        .filter(AuditAnswer.audit_execution_id.in_(execution_ids))
        .all()
    )

    total = len(answers)
    ok = sum(1 for a in answers if a.odpoved == "ok")
    nok = sum(1 for a in answers if a.odpoved == "nok")

    neshody = (
        db.query(Neshoda)
        .filter(Neshoda.audit_execution_id.in_(execution_ids))
        .all()
    )

    open_neshody = sum(1 for n in neshody if n.status != "closed")

    return {
        "kpi": {
            "audits_count": len(executions),
            "total_questions": total,
            "ok": ok,
            "nok": nok,
            "percent_ok": round((ok / total) * 100 if total else 0, 1),
            "neshody_total": len(neshody),
            "neshody_open": open_neshody,
        }
    }
