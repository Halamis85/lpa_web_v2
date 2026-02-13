from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_db, get_current_user
from ..models import LpaAssignment, LpaCampaign, Line, ChecklistCategory, User

router = APIRouter()

@router.get("/matrix/{month}")
def allocation_matrix(
    month: str,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    campaign = db.query(LpaCampaign).filter_by(month=month).first()
    if not campaign:
        return {"lines": [], "auditors": [], "matrix": []}

    assignments = (
        db.query(LpaAssignment, Line, ChecklistCategory, User)
        .join(Line, Line.id == LpaAssignment.line_id)
        .join(ChecklistCategory, ChecklistCategory.id == LpaAssignment.category_id)
        .join(User, User.id == LpaAssignment.auditor_id)
        .filter(LpaAssignment.campaign_id == campaign.id)
        .all()
    )

    # unikátní seznamy
    lines = sorted({l.name for _, l, _, _ in assignments})
    auditors = sorted({u.jmeno for _, _, _, u in assignments})

    # matice
    matrix = {a: {l: "" for l in lines} for a in auditors}

    for assignment, line, category, user in assignments:
        matrix[user.jmeno][line.name] = category.name

    return {
        "lines": lines,
        "auditors": auditors,
        "matrix": matrix,
    }
