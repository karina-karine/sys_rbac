from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Department
from app.schemas import DepartmentCreate, DepartmentResponse
from app.auth import get_current_user, require_permission

router = APIRouter()

@router.get("/", response_model=List[DepartmentResponse])
async def get_departments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("departments.read"))
):
    """Отримання списку відділень"""
    departments = db.query(Department).filter(Department.is_active == True).offset(skip).limit(limit).all()
    return departments

@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("departments.read"))
):
    """Отримання відділення за ID"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Відділення не знайдено")
    return department

@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("departments.create"))
):
    """Створення нового відділення"""
    db_department = Department(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department
