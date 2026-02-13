from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime

from ..auth import get_db, get_current_user
from ..models import (
    AuditExecution,
    ChecklistQuestion,
    AuditAnswer,
    Neshoda,
    User,
)

router = APIRouter()

@router.post("/")
def save_answer(
    audit_execution_id: int = Form(...),
    question_id: int = Form(...),
    odpoved: str = Form(...),          # "OK" / "NOK"
    has_issue: bool = Form(False),
    poznamka: str | None = Form(None),
    picture: UploadFile | None = File(None),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # --- VALIDACE ---

    execution = (
        db.query(AuditExecution)
        .filter(AuditExecution.id == audit_execution_id)
        .first()
    )
    if not execution:
        raise HTTPException(status_code=404, detail="Audit nenalezen")

    if execution.auditor_id != current.id and current.role != "admin":
        raise HTTPException(status_code=403, detail="Nemůžeš zapisovat cizí audit")

    question = (
        db.query(ChecklistQuestion)
        .filter(ChecklistQuestion.id == question_id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Otázka nenalezena")

    # Normalizace odpovědi
    odpoved_norm = odpoved.strip().upper()
    if odpoved_norm not in ["OK", "NOK"]:
        raise HTTPException(
            status_code=400,
            detail="Odpověď musí být 'OK' nebo 'NOK'",
        )

    # --- ULOŽENÍ ODPOVĚDI (UPSERT = insert nebo update) ---

    existing = (
        db.query(AuditAnswer)
        .filter(
            AuditAnswer.audit_execution_id == audit_execution_id,
            AuditAnswer.question_id == question_id,
        )
        .first()
    )

    if existing:
        existing.odpoved = odpoved_norm
        existing.has_issue = has_issue
        existing.picture_url = existing.picture_url  # zatím beze změny
    else:
        ans = AuditAnswer(
            audit_execution_id=audit_execution_id,
            question_id=question_id,
            odpoved=odpoved_norm,
            has_issue=has_issue,
        )
        db.add(ans)

    # --- AUTOMATICKÁ NESHODA PŘI NOK ---

    if odpoved_norm == "NOK":
        neshoda = Neshoda(
            audit_execution_id=audit_execution_id,
            popis=poznamka or "Zjištěna neshoda při auditu",
            zavaznost="medium",
            status="open",
        )
        db.add(neshoda)

    #-----Přidání fotky--------
   
    picture_path = None

    if picture:
        import os
        from uuid import uuid4

        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        date_str = datetime.utcnow().strftime("%Y%m%d")
        filename = f"{date_str}_{audit_execution_id}_{question_id}_01{os.path.splitext(picture.filename)[1]}"
        file_path = os.path.join(upload_dir, filename)      

        with open(file_path, "wb") as f:
            f.write(picture.file.read())

        picture_path = file_path

    # Uložíme cestu k fotce do odpovědi
        if existing:
            existing.picture_url = picture_path
        else:
            ans.picture_url = picture_path

    db.commit()

    return {"message": "Odpověď uložena"}

@router.get("/summary/{audit_execution_id}")
def audit_summary(
    audit_execution_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    answers = (
        db.query(AuditAnswer)
        .filter(AuditAnswer.audit_execution_id == audit_execution_id)
        .all()
    )

    if not answers:
        return {
            "total": 0,
            "ok": 0,
            "nok": 0,
            "ok_percent": 0,
            "nok_questions": [],
        }

    total = len(answers)
    ok_count = sum(1 for a in answers if a.odpoved == "OK")
    nok_count = total - ok_count
    ok_percent = round((ok_count / total) * 100, 1)

    # seznam otázek, kde bylo NOK (volitelné, ale užitečné)
    nok_questions = [
        {
            "question_id": a.question_id,
            "picture_url": a.picture_url,
        }
        for a in answers
        if a.odpoved == "NOK"
    ]

    return {
        "total": total,
        "ok": ok_count,
        "nok": nok_count,
        "ok_percent": ok_percent,
        "nok_questions": nok_questions,
    }
