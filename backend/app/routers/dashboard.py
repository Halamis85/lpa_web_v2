from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from collections import defaultdict


from ..auth import get_db, get_current_user
from ..models import (
    AuditAnswer,
    AuditExecution,
    LpaAssignment,
    LpaCampaign,
    Line,
    ChecklistCategory,
    ChecklistQuestion,
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
        db.query(AuditExecution).filter(AuditExecution.status == "done").count()
    )

    # OK / NOK odpovědi
    ok_count = db.query(AuditAnswer).filter(AuditAnswer.odpoved == "OK").count()

    nok_count = db.query(AuditAnswer).filter(AuditAnswer.odpoved == "NOK").count()

    total_answers = ok_count + nok_count
    percent_ok = round((ok_count / total_answers) * 100, 1) if total_answers > 0 else 0

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
        db.query(
            AuditExecution, LpaAssignment, LpaCampaign, Line, ChecklistCategory, User
        )
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
        result.append(
            {
                "id": exec.id,
                "month": campaign.month,
                "line": line.name,
                "category": category.name,
                "auditor": auditor.jmeno,
                "status": exec.status,
            }
        )

    return result


# --- Pro graf --
@router.get("/stats/monthly-audits")
def get_monthly_audits(
    months: int = 6,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Graf: Počet provedených auditů za posledních X měsíců"""
    today = date.today()
    result = []

    for i in range(months - 1, -1, -1):
        month_date = today.replace(day=1) - timedelta(days=30 * i)
        month_str = month_date.strftime("%Y-%m")

        # Spočítej audity pro tento měsíc
        campaigns = (
            db.query(LpaCampaign.id).filter(LpaCampaign.month == month_str).subquery()
        )

        completed = (
            db.query(AuditExecution)
            .join(LpaAssignment, LpaAssignment.id == AuditExecution.assignment_id)
            .filter(
                LpaAssignment.campaign_id.in_(campaigns),
                AuditExecution.status == "done",
            )
            .count()
        )

        in_progress = (
            db.query(AuditExecution)
            .join(LpaAssignment, LpaAssignment.id == AuditExecution.assignment_id)
            .filter(
                LpaAssignment.campaign_id.in_(campaigns),
                AuditExecution.status == "in_progress",
            )
            .count()
        )

        result.append(
            {
                "month": month_str,
                "month_label": month_date.strftime("%B %Y"),
                "completed": completed,
                "in_progress": in_progress,
                "total": completed + in_progress,
            }
        )

    return result


@router.get("/stats/success-rate-trend")
def get_success_rate_trend(
    months: int = 6,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Graf: Trend úspěšnosti (% OK odpovědí) v čase"""
    today = date.today()
    result = []

    for i in range(months - 1, -1, -1):
        month_date = today.replace(day=1) - timedelta(days=30 * i)
        month_str = month_date.strftime("%Y-%m")

        # Najdi všechny executiony pro tento měsíc
        campaigns = (
            db.query(LpaCampaign.id).filter(LpaCampaign.month == month_str).subquery()
        )

        executions = (
            db.query(AuditExecution.id)
            .join(LpaAssignment, LpaAssignment.id == AuditExecution.assignment_id)
            .filter(LpaAssignment.campaign_id.in_(campaigns))
            .subquery()
        )

        ok_count = (
            db.query(AuditAnswer)
            .filter(
                AuditAnswer.audit_execution_id.in_(executions),
                AuditAnswer.odpoved == "OK",
            )
            .count()
        )

        nok_count = (
            db.query(AuditAnswer)
            .filter(
                AuditAnswer.audit_execution_id.in_(executions),
                AuditAnswer.odpoved == "NOK",
            )
            .count()
        )

        total = ok_count + nok_count
        success_rate = round((ok_count / total * 100), 1) if total > 0 else 0

        result.append(
            {
                "month": month_str,
                "month_label": month_date.strftime("%b %Y"),
                "success_rate": success_rate,
                "ok": ok_count,
                "nok": nok_count,
                "total": total,
            }
        )

    return result


@router.get("/stats/by-line")
def get_stats_by_line(
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Graf: Statistiky podle linek"""
    lines_data = (
        db.query(
            Line.name.label("line_name"),
            func.count(AuditExecution.id).label("audit_count"),
        )
        .join(LpaAssignment, LpaAssignment.line_id == Line.id)
        .join(AuditExecution, AuditExecution.assignment_id == LpaAssignment.id)
        .filter(AuditExecution.status == "done")
        .group_by(Line.name)
        .all()
    )

    result = []
    for line_name, audit_count in lines_data:
        # Spočítej OK/NOK pro tuto linku
        executions = (
            db.query(AuditExecution.id)
            .join(LpaAssignment, LpaAssignment.id == AuditExecution.assignment_id)
            .join(Line, Line.id == LpaAssignment.line_id)
            .filter(Line.name == line_name, AuditExecution.status == "done")
            .subquery()
        )

        ok_count = (
            db.query(AuditAnswer)
            .filter(
                AuditAnswer.audit_execution_id.in_(executions),
                AuditAnswer.odpoved == "OK",
            )
            .count()
        )

        nok_count = (
            db.query(AuditAnswer)
            .filter(
                AuditAnswer.audit_execution_id.in_(executions),
                AuditAnswer.odpoved == "NOK",
            )
            .count()
        )

        total = ok_count + nok_count
        success_rate = round((ok_count / total * 100), 1) if total > 0 else 0

        result.append(
            {
                "line_name": line_name,
                "audit_count": audit_count,
                "ok": ok_count,
                "nok": nok_count,
                "success_rate": success_rate,
            }
        )

    return sorted(result, key=lambda x: x["audit_count"], reverse=True)


@router.get("/stats/by-auditor")
def get_stats_by_auditor(
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Graf: Statistiky podle auditorů"""
    auditor_data = (
        db.query(
            User.jmeno.label("auditor_name"),
            func.count(AuditExecution.id).label("audit_count"),
        )
        .join(LpaAssignment, LpaAssignment.auditor_id == User.id)
        .join(AuditExecution, AuditExecution.assignment_id == LpaAssignment.id)
        .filter(AuditExecution.status == "done", User.role == "auditor")
        .group_by(User.jmeno)
        .all()
    )

    result = []
    for auditor_name, audit_count in auditor_data:
        # Spočítej OK/NOK pro tohoto auditora
        executions = (
            db.query(AuditExecution.id)
            .join(LpaAssignment, LpaAssignment.id == AuditExecution.assignment_id)
            .join(User, User.id == LpaAssignment.auditor_id)
            .filter(User.jmeno == auditor_name, AuditExecution.status == "done")
            .subquery()
        )

        ok_count = (
            db.query(AuditAnswer)
            .filter(
                AuditAnswer.audit_execution_id.in_(executions),
                AuditAnswer.odpoved == "OK",
            )
            .count()
        )

        nok_count = (
            db.query(AuditAnswer)
            .filter(
                AuditAnswer.audit_execution_id.in_(executions),
                AuditAnswer.odpoved == "NOK",
            )
            .count()
        )

        total = ok_count + nok_count
        success_rate = round((ok_count / total * 100), 1) if total > 0 else 0

        result.append(
            {
                "auditor_name": auditor_name,
                "audit_count": audit_count,
                "ok": ok_count,
                "nok": nok_count,
                "success_rate": success_rate,
            }
        )

    return sorted(result, key=lambda x: x["audit_count"], reverse=True)


@router.get("/stats/by-category")
def get_stats_by_category(
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Graf: NOK podle kategorií"""
    category_data = (
        db.query(
            ChecklistCategory.name.label("category_name"),
            func.count(AuditAnswer.id).label("nok_count"),
        )
        .join(ChecklistQuestion, ChecklistQuestion.category_id == ChecklistCategory.id)
        .join(AuditAnswer, AuditAnswer.question_id == ChecklistQuestion.id)
        .filter(AuditAnswer.odpoved == "NOK")
        .group_by(ChecklistCategory.name)
        .all()
    )

    result = []
    for category_name, nok_count in category_data:
        result.append({"category_name": category_name, "nok_count": nok_count})

    return sorted(result, key=lambda x: x["nok_count"], reverse=True)


@router.get("/stats/overall")
def get_overall_statistics(
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Celkové KPI statistiky"""

    # Celkem dokončených auditů
    total_audits = (
        db.query(AuditExecution).filter(AuditExecution.status == "done").count()
    )

    # Celkem probíhajících
    in_progress = (
        db.query(AuditExecution).filter(AuditExecution.status == "in_progress").count()
    )

    # Celkem odpovědí
    total_answers = db.query(AuditAnswer).count()

    # OK / NOK
    ok_count = db.query(AuditAnswer).filter(AuditAnswer.odpoved == "OK").count()

    nok_count = db.query(AuditAnswer).filter(AuditAnswer.odpoved == "NOK").count()

    # Úspěšnost
    success_rate = (
        round((ok_count / total_answers * 100), 1) if total_answers > 0 else 0
    )

    # Průměrná úspěšnost za poslední měsíc
    today = date.today()
    month_start = today.replace(day=1)

    recent_executions = (
        db.query(AuditExecution.id)
        .filter(
            AuditExecution.started_at >= month_start, AuditExecution.status == "done"
        )
        .subquery()
    )

    recent_ok = (
        db.query(AuditAnswer)
        .filter(
            AuditAnswer.audit_execution_id.in_(recent_executions),
            AuditAnswer.odpoved == "OK",
        )
        .count()
    )

    recent_nok = (
        db.query(AuditAnswer)
        .filter(
            AuditAnswer.audit_execution_id.in_(recent_executions),
            AuditAnswer.odpoved == "NOK",
        )
        .count()
    )

    recent_total = recent_ok + recent_nok
    recent_success_rate = (
        round((recent_ok / recent_total * 100), 1) if recent_total > 0 else 0
    )

    return {
        "total_audits": total_audits,
        "in_progress": in_progress,
        "total_answers": total_answers,
        "ok_count": ok_count,
        "nok_count": nok_count,
        "success_rate": success_rate,
        "recent_month_success_rate": recent_success_rate,
        "recent_month_audits": db.query(AuditExecution)
        .filter(
            AuditExecution.started_at >= month_start, AuditExecution.status == "done"
        )
        .count(),
    }
