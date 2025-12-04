from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn

from app.database import engine, Base, get_db
from app.routers import auth, users, patients, appointments, medical_records, departments, rbac
from app.models import User, Role, Permission
from app.auth import create_access_token
from app.rbac import init_rbac_system

# Створення таблиць в БД
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ініціалізація системи при запуску"""
    # Startup
    db = next(get_db())
    init_rbac_system(db)
    print("✓ Система RBAC ініціалізована")
    print("✓ Сервер запущено на http://localhost:8000")
    print("✓ Документація API: http://localhost:8000/docs")
    yield
    # Shutdown (якщо потрібно щось зробити при зупинці)
    print("✓ Сервер зупинено")

app = FastAPI(
    title="Система управління закладом охорони здоров'я",
    description="Інформаційна технологія автоматизації процесів управління діяльністю ЗОЗ на основі моделі RBAC",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення роутерів
app.include_router(auth.router, prefix="/api/auth", tags=["Аутентифікація"])
app.include_router(users.router, prefix="/api/users", tags=["Користувачі"])
app.include_router(patients.router, prefix="/api/patients", tags=["Пацієнти"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Записи на прийом"])
app.include_router(medical_records.router, prefix="/api/medical-records", tags=["Медичні записи"])
app.include_router(departments.router, prefix="/api/departments", tags=["Відділення"])
app.include_router(rbac.router, prefix="/api/rbac", tags=["Управління доступом"])

# Статичні файли
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Головна сторінка"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/health")
async def health_check():
    """Перевірка стану системи"""
    return {
        "status": "healthy",
        "message": "Система управління ЗОЗ працює"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
