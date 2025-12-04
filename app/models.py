from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Boolean, Text, Date, Time, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

# Таблиця зв'язку many-to-many для користувачів і ролей
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# Таблиця зв'язку many-to-many для ролей і дозволів
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class User(Base):
    """Модель користувача системи"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Зв'язки
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    created_appointments = relationship("Appointment", foreign_keys="Appointment.created_by_id", back_populates="created_by")
    medical_records_created = relationship("MedicalRecord", back_populates="doctor")
    
    def has_permission(self, permission_name: str) -> bool:
        """Перевірка наявності дозволу у користувача"""
        for role in self.roles:
            if any(perm.name == permission_name for perm in role.permissions):
                return True
        return False
    
    def has_role(self, role_name: str) -> bool:
        """Перевірка наявності ролі у користувача"""
        return any(role.name == role_name for role in self.roles)

class Role(Base):
    """Модель ролі в системі RBAC"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    priority = Column(Integer, default=0)  # Пріоритет ролі (чим вище, тим більше прав)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Зв'язки
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    """Модель дозволу в системі RBAC"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    resource = Column(String)  # Ресурс (users, patients, appointments тощо)
    action = Column(String)    # Дія (create, read, update, delete)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Зв'язки
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class Patient(Base):
    """Модель пацієнта"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String)
    birth_date = Column(Date, nullable=False)
    gender = Column(String)
    phone = Column(String, nullable=False)
    email = Column(String)
    address = Column(String)
    insurance_number = Column(String, unique=True)
    blood_type = Column(String)
    allergies = Column(Text)
    chronic_diseases = Column(Text)
    emergency_contact = Column(String)
    emergency_phone = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Зв'язки
    appointments = relationship("Appointment", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")

class Department(Base):
    """Модель відділення лікарні"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    phone = Column(String)
    floor = Column(Integer)
    capacity = Column(Integer)
    head_doctor_id = Column(Integer, ForeignKey('users.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Зв'язки
    appointments = relationship("Appointment", back_populates="department")

class AppointmentStatus(enum.Enum):
    """Статуси записів на прийом"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class Appointment(Base):
    """Модель запису на прийом"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'))
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(String, default=AppointmentStatus.SCHEDULED.value)
    reason = Column(Text)
    notes = Column(Text)
    created_by_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Зв'язки
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", foreign_keys=[doctor_id])
    department = relationship("Department", back_populates="appointments")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_appointments")

class MedicalRecord(Base):
    """Модель медичного запису"""
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    visit_date = Column(DateTime, default=datetime.utcnow)
    diagnosis = Column(Text, nullable=False)
    symptoms = Column(Text)
    treatment = Column(Text)
    prescriptions = Column(Text)
    lab_results = Column(Text)
    notes = Column(Text)
    is_confidential = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Зв'язки
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("User", back_populates="medical_records_created")
