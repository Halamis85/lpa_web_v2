from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..auth import get_db, get_current_user
from ..models import (
    AuditAnswer,
    AuditExecution,
    LpaAssignment,
    LpaCampaign,
    Line,
    ChecklistCategory,
    User,
)

router = APIRouter()


# ==============================
# GET /dashboard/kpi
# ==============================
@router.get("/kpi")
def get_kpi(
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Celkem auditů (dokončených)
    audits_count = (
        db.query(AuditExecution)
        .filter(AuditExecution.status == "done")
        .count()
    )

    # OK / NOK odpovědi
    ok_count = (
        db.query(AuditAnswer)
        .filter(AuditAnswer.odpoved == "OK")
        .count()
    )

    nok_count = (
        db.query(AuditAnswer)
        .filter(AuditAnswer.odpoved == "NOK")
        .count()
    )

    total_answers = ok_count + nok_count
    percent_ok = (
        round((ok_count / total_answers) * 100, 1)
        if total_answers > 0
        else 0
    )

    return {
        "audits_count": audits_count,
        "ok": ok_count,
        "nok": nok_count,
        "percent_ok": percent_ok,
    }


# ==============================
# GET /dashboard/last-audits
# ==============================
@router.get("/last-audits")
def get_last_audits(
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Posledních 5 auditů (podle času zahájení)
    executions = (
        db.query(AuditExecution, LpaAssignment, LpaCampaign, Line, ChecklistCategory, User)
        .join(LpaAssignment, LpaAssignment.id == AuditExecution.assignment_id)
        .join(LpaCampaign, LpaCampaign.id == LpaAssignment.campaign_id)
        .join(Line, Line.id == LpaAssignment.line_id)
        .join(ChecklistCategory, ChecklistCategory.id == LpaAssignment.category_id)
        .join(User, User.id == LpaAssignment.auditor_id)
        .order_by(AuditExecution.started_at.desc())
        .limit(5)
        .all()
    )

    result = []
    for exec, assignment, campaign, line, category, auditor in executions:
        result.append({
            "id": exec.id,
            "month": campaign.month,
            "line": line.name,
            "category": category.name,
            "auditor": auditor.jmeno,
            "status": exec.status,
        })

    return result

#--- Pro graf --
from datetime import date, timedelta

@router.get("/trend")
def get_trend(
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Posledních 6 měsíců
    today = date.today()
    months = []
    for i in range(5, -1, -1):
        m = (today.replace(day=1) - timedelta(days=30*i)).strftime("%Y-%m")
        months.append(m)

    data = []

    for m in months:
        # Najdeme kampaně v daném měsíci
        campaigns = db.query(LpaCampaign.id).filter(LpaCampaign.month == m).subquery()

        # Najdeme executiony z těchto kampaní
        executions = (
            db.query(AuditExecution.id)
            .join(LpaAssignment, LpaAssignment.id == AuditExecution.assignment_id)
            .filter(LpaAssignment.campaign_id.in_(campaigns))
            .subquery()
        )

        ok = (
            db.query(AuditAnswer)
            .filter(
                AuditAnswer.audit_execution_id.in_(executions),
                AuditAnswer.odpoved == "OK",
            )
            .count()
        )

        nok = (
            db.query(AuditAnswer)
            .filter(
                AuditAnswer.audit_execution_id.in_(executions),
                AuditAnswer.odpoved == "NOK",
            )
            .count()
        )

        data.append({
            "month": m,
            "ok": ok,
            "nok": nok,
        })

    return data
