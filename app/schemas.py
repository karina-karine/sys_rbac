from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, date, time
from typing import Optional, List

# ===== AUTH SCHEMAS =====
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

# ===== USER SCHEMAS =====
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: int
    priority: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    roles: List[RoleResponse] = []
    
    class Config:
        from_attributes = True

# ===== PERMISSION SCHEMAS =====
class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str
    action: str

class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RolePermissionsResponse(RoleResponse):
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True

# ===== PATIENT SCHEMAS =====
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    birth_date: date
    gender: Optional[str] = None
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    insurance_number: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    chronic_diseases: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    chronic_diseases: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    is_active: Optional[bool] = None

class PatientResponse(PatientBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== DEPARTMENT SCHEMAS =====
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    phone: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    head_doctor_id: Optional[int] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== APPOINTMENT SCHEMAS =====
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    department_id: Optional[int] = None
    appointment_date: date
    appointment_time: time
    duration_minutes: int = 30
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: int
    status: str
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== MEDICAL RECORD SCHEMAS =====
class MedicalRecordBase(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    diagnosis: str
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    prescriptions: Optional[str] = None
    lab_results: Optional[str] = None
    notes: Optional[str] = None
    is_confidential: bool = False

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordUpdate(BaseModel):
    diagnosis: Optional[str] = None
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    prescriptions: Optional[str] = None
    lab_results: Optional[str] = None
    notes: Optional[str] = None
    is_confidential: Optional[bool] = None

class MedicalRecordResponse(MedicalRecordBase):
    id: int
    doctor_id: int
    visit_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
