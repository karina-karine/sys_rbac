from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, MedicalRecord, Patient
from app.schemas import MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse
from app.auth import get_current_user, require_permission

router = APIRouter()

@router.get("/", response_model=List[MedicalRecordResponse])
async def get_medical_records(
    skip: int = 0,
    limit: int = 100,
    patient_id: int = None,
    doctor_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("medical_records.read"))
):
    """
    Отримання медичних записів з фільтрацією
    """
    query = db.query(MedicalRecord)
    
    # Лікарі бачать тільки свої записи, якщо не мають повного доступу
    if not current_user.has_role("Адміністратор"):
        if current_user.has_role("Лікар") and not doctor_id:
            query = query.filter(MedicalRecord.doctor_id == current_user.id)
    
    if patient_id:
        query = query.filter(MedicalRecord.patient_id == patient_id)
    if doctor_id:
        query = query.filter(MedicalRecord.doctor_id == doctor_id)
    
    records = query.offset(skip).limit(limit).all()
    return records

@router.get("/{record_id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("medical_records.read"))
):
    """Отримання медичного запису за ID"""
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    
    # Перевірка доступу до конфіденційних записів
    if record.is_confidential and not current_user.has_role("Адміністратор"):
        if record.doctor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ до конфіденційного запису заборонено"
            )
    
    return record

@router.post("/", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    record: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("medical_records.create"))
):
    """Створення медичного запису"""
    # Перевірка існування пацієнта
    patient = db.query(Patient).filter(Patient.id == record.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    
    db_record = MedicalRecord(
        **record.model_dump(),
        doctor_id=current_user.id
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.put("/{record_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    record_id: int,
    record_update: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("medical_records.update"))
):
    """Оновлення медичного запису"""
    db_record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    
    # Лікар може редагувати тільки свої записи
    if not current_user.has_role("Адміністратор"):
        if db_record.doctor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ви можете редагувати тільки свої записи"
            )
    
    update_data = record_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record

@router.delete("/{record_id}")
async def delete_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("medical_records.delete"))
):
    """Видалення медичного запису"""
    db_record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    
    # Тільки адміністратор може видаляти медичні записи
    if not current_user.has_role("Адміністратор"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостатньо прав для видалення"
        )
    
    db.delete(db_record)
    db.commit()
    return {"message": "Медичний запис видалено"}
