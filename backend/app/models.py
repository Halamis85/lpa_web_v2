from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .database import Base


# ===========================
# USERS
# ===========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    jmeno = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    password_hash = Column(String, nullable=True)

    # ✅ PŘIDEJTE TYTO DVA SLOUPCE
    roles = Column(String, nullable=True)
    force_password_change = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    # ✅ PŘIDEJTE TYTO DVĚ METODY
    def has_role(self, role_name: str) -> bool:
        """Zkontroluje, zda má uživatel danou roli"""
        if not self.roles:
            return self.role == role_name
        return role_name in self.roles.split(",")

    def get_roles_list(self) -> list:
        """Vrátí seznam všech rolí"""
        if not self.roles:
            return [self.role]
        return self.roles.split(",")


# ===========================
# AREAS (LINKY / OBLASTI)
# ===========================
class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)


# ===========================
# LPA CAMPAIGN (MĚSÍČNÍ KAMPAŇ)
# ===========================
class LpaCampaign(Base):
    __tablename__ = "lpa_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, nullable=False)  # "2026-03"
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="draft")  # draft / active / closed


# ===========================
# MĚSÍČNÍ PŘIDĚLENÍ (ROZPIS LPA)
# ===========================
class LpaAssignment(Base):
    __tablename__ = "lpa_assignments"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("lpa_campaigns.id"))
    auditor_id = Column(Integer, ForeignKey("users.id"))
    line_id = Column(Integer, ForeignKey("lines.id"))
    template_id = Column(Integer, ForeignKey("checklist_templates.id"), nullable=True)
    termin = Column(Date, nullable=False)
    datum_provedeni = Column(Date, nullable=True)
    status = Column(String, default="pending")  # pending / in_progress / done
    category_id = Column(Integer, ForeignKey("checklist_categories.id"), nullable=True)


# ===========================
# SKUTEČNÉ PROVEDENÍ AUDITU
# ===========================
class AuditExecution(Base):
    __tablename__ = "audit_execution"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("lpa_assignments.id"))
    auditor_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String, default="in_progress")  # in_progress / done


# ===========================
# CHECKLIST – ŠABLONY
# ===========================
class ChecklistTemplate(Base):
    __tablename__ = "checklist_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    line_id = Column(Integer, ForeignKey("lines.id"), nullable=False)


# ===========================
# CHECKLIST – kategorie
# ===========================
class ChecklistCategory(Base):
    __tablename__ = "checklist_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)


# ===========================
# CHECKLIST – OTÁZKY
# ===========================
class ChecklistQuestion(Base):
    __tablename__ = "checklist_questions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("checklist_templates.id"))
    category_id = Column(Integer, ForeignKey("checklist_categories.id"))
    question_text = Column(String, nullable=False)
    position = Column(Integer, nullable=False)  # 1,2,3,4 = řádek v Excelu


# ===========================
# ODPOVĚDI AUDITORA
# ===========================
class AuditAnswer(Base):
    __tablename__ = "audit_answers"

    id = Column(Integer, primary_key=True, index=True)
    audit_execution_id = Column(Integer, ForeignKey("audit_execution.id"))
    question_id = Column(Integer, ForeignKey("checklist_questions.id"))
    odpoved = Column(String, nullable=True)
    picture_url = Column(String, nullable=True)
    has_issue = Column(Boolean, default=False)


# ===========================
# NESHODY (WORKFLOW)
# ===========================
class Neshoda(Base):
    __tablename__ = "neshody"

    id = Column(Integer, primary_key=True, index=True)
    audit_execution_id = Column(Integer, ForeignKey("audit_execution.id"))

    popis = Column(String, nullable=False)
    zavaznost = Column(String)  # low / medium / high

    status = Column(
        String, default="open"
    )  # open / assigned / in_progress / resolved / closed

    solver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    termin = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    assigned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    poznamka = Column(String, nullable=True)


# ============================================
# Výrobní linky
# ===========================================
class Line(Base):
    __tablename__ = "lines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
