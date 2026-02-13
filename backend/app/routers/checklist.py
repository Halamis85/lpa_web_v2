from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_db, get_current_user
from ..models import ChecklistTemplate, ChecklistQuestion, ChecklistCategory, User


router = APIRouter()

# ======= ŠABLONY CHECKLISTU =======

@router.post("/templates")
def create_checklist_template(
    name: str,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    existing = (
        db.query(ChecklistTemplate)
        .filter(ChecklistTemplate.name == name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Template already exists")

    template = ChecklistTemplate(name=name)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/templates")
def list_checklist_templates(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(ChecklistTemplate).all()


@router.get("/templates/{template_id}")
def get_checklist_template(
    template_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    template = (
        db.query(ChecklistTemplate)
        .filter(ChecklistTemplate.id == template_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


# ======= OTÁZKY V CHECKLISTU =======

@router.post("/questions")
def add_question(
    template_id: int,
    category_id: int,
    question_text: str,
    position: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    template = db.query(ChecklistTemplate).filter_by(id=template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Checklist template not found")

    category = db.query(ChecklistCategory).filter_by(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Zabráníme duplicitě na stejné pozici
    existing = (
        db.query(ChecklistQuestion)
        .filter(
            ChecklistQuestion.template_id == template_id,
            ChecklistQuestion.category_id == category_id,
            ChecklistQuestion.position == position,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Otázka na této pozici už existuje"
        )

    question = ChecklistQuestion(
        template_id=template_id,
        category_id=category_id,
        question_text=question_text,
        position=position,
    )

    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.get("/{template_id}/questions")
def list_questions(
    template_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(ChecklistQuestion)
        .filter(ChecklistQuestion.template_id == template_id)
        .all()
    )

@router.post("/templates/for-line")
def get_or_create_template_for_line(
    line_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    # Zkusíme najít existující šablonu pro tuto linku
    template = (
        db.query(ChecklistTemplate)
        .filter(ChecklistTemplate.line_id == line_id)
        .first()
    )

    if template:
        return template  # už existuje

    # Pokud neexistuje → vytvoříme ji
    template = ChecklistTemplate(
        name=f"Checklist for line {line_id}",
        line_id=line_id,
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return template

@router.get("/templates/{template_id}/questions")
def list_questions_for_template(
    template_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    questions = (
        db.query(ChecklistQuestion, ChecklistCategory.name.label("category_name"))
        .join(ChecklistCategory, ChecklistQuestion.category_id == ChecklistCategory.id)
        .filter(ChecklistQuestion.template_id == template_id)
        .order_by(ChecklistQuestion.category_id, ChecklistQuestion.position)
        .all()
    )

    # Přemapujeme do čistého JSON formátu pro Vue
    result = []
    for q, cat_name in questions:
        result.append({
            "id": q.id,
            "template_id": q.template_id,
            "category_id": q.category_id,
            "category_name": cat_name,   # 🔹 KLÍČOVÉ
            "question_text": q.question_text,
            "position": q.position,
        })

    return result
@router.get("/categories")
def list_categories(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(ChecklistCategory).all()

@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    q = db.query(ChecklistQuestion).filter_by(id=question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(q)
    db.commit()
    return {"deleted": question_id}

@router.patch("/questions/{question_id}")
def update_question(
    question_id: int,
    question_text: str,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin")

    q = db.query(ChecklistQuestion).filter_by(id=question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    q.question_text = question_text
    db.commit()
    db.refresh(q)
    return q
