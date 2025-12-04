from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Patient
from app.schemas import PatientCreate, PatientUpdate, PatientResponse
from app.auth import get_current_user, require_permission

router = APIRouter()

@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("patients.read"))
):
    """
    Отримання списку пацієнтів з можливістю пошуку
    """
    query = db.query(Patient)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Patient.first_name.ilike(search_filter)) |
            (Patient.last_name.ilike(search_filter)) |
            (Patient.phone.ilike(search_filter)) |
            (Patient.email.ilike(search_filter))
        )
    
    patients = query.offset(skip).limit(limit).all()
    return patients

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("patients.read"))
):
    """Отримання пацієнта за ID"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    return patient

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("patients.create"))
):
    """Додавання нового пацієнта"""
    # Перевірка унікальності страхового номера
    if patient.insurance_number:
        existing = db.query(Patient).filter(
            Patient.insurance_number == patient.insurance_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пацієнт з таким страховим номером вже існує"
            )
    
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("patients.update"))
):
    """Оновлення даних пацієнта"""
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    
    update_data = patient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("patients.delete"))
):
    """Видалення пацієнта"""
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    
    # М'яке видалення - деактивація
    db_patient.is_active = False
    db.commit()
    return {"message": "Пацієнта деактивовано"}
