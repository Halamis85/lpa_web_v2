from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import dashboard
from .routers import allocations

from .database import engine, Base

from .routers import (
    users,
    areas,
    lines,
    campaigns,
    assignments,
    checklist,
    answers,
    neshody,
    auth,
)
from .routers import executions


app = FastAPI(title="LPA v2 API", redirect_slashes=False)

# ---- CORS pro Vue ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Vytvoření tabulek (prozatím – později přejdeme na Alembic)
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "LPA v2 backend running"}


# ====== REGISTRACE ROUTERŮ ======
app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(areas.router, prefix="/areas", tags=["areas"])
app.include_router(lines.router, prefix="/lines", tags=["lines"])
app.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
app.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
app.include_router(checklist.router, prefix="/checklist", tags=["checklist"])
app.include_router(answers.router, prefix="/answers", tags=["answers"])
app.include_router(neshody.router, prefix="/neshody", tags=["neshody"])
app.include_router(executions.router, prefix="/executions", tags=["executions"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(allocations.router, prefix="/allocations", tags=["allocations"])
