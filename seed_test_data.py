"""
Скрипт для заповнення системи тестовими даними
Для демонстрації функціоналу системи управління закладом охорони здоров'я
"""
import sys
from datetime import datetime, timedelta, time
from random import choice, randint
from sqlalchemy.orm import Session
from app.database import engine, Base
from app.models import User, Patient, Appointment, MedicalRecord, Department, Role
from app.auth import get_password_hash

def seed_test_data():
    """Заповнення бази даних тестовими даними"""
    
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)

    try:
        print("🏥 Початок заповнення тестовими даними...")

        # 1. Ролі (перевірка наявності)
        def get_or_create_role(name, description=""):
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                role = Role(name=name, description=description)
                db.add(role)
                db.commit()
            return role

        admin_role = get_or_create_role("Адміністратор")
        doctor_role = get_or_create_role("Лікар")
        nurse_role = get_or_create_role("Медсестра")
        receptionist_role = get_or_create_role("Реєстратор")

        # 2. Відділення
        print("\n📋 Створення відділень...")
        departments_data = [
            {"name": "Кардіологія", "description": "Відділення серцево-судинних захворювань", "phone": "+380441234567", "floor": 2, "capacity": 15},
            {"name": "Неврологія", "description": "Відділення нервових захворювань", "phone": "+380441234568", "floor": 3, "capacity": 12},
            {"name": "Педіатрія", "description": "Дитяче відділення", "phone": "+380441234569", "floor": 1, "capacity": 20},
            {"name": "Хірургія", "description": "Хірургічне відділення", "phone": "+380441234570", "floor": 4, "capacity": 10},
            {"name": "Терапія", "description": "Терапевтичне відділення", "phone": "+380441234571", "floor": 2, "capacity": 18}
        ]

        departments = []
        for dept_data in departments_data:
            dept = db.query(Department).filter(Department.name == dept_data["name"]).first()
            if not dept:
                dept = Department(**dept_data)
                db.add(dept)
                db.commit()
            departments.append(dept)
        print(f"✅ Створено {len(departments)} відділень")

        # 3. Пацієнти
        print("\n🏥 Створення пацієнтів...")
        patients_data = [
            {"first_name": "Василь", "last_name": "Шевченко", "middle_name": "Григорович",
             "birth_date": datetime(1975, 3, 15).date(), "gender": "Чоловік", "phone": "+380501234567",
             "email": "v.shevchenko@gmail.com", "address": "м. Київ, вул. Хрещатик, 25, кв. 10",
             "emergency_contact": "Шевченко Оксана (дружина) +380501234568", "blood_type": "A+", "allergies": "Пеніцилін"},
            {"first_name": "Оксана", "last_name": "Коваль", "middle_name": "Петрівна",
             "birth_date": datetime(1990, 7, 22).date(), "gender": "Жінка", "phone": "+380501234569",
             "email": "o.koval@gmail.com", "address": "м. Київ, вул. Саксаганського, 45",
             "emergency_contact": "Коваль Петро (батько) +380501234570", "blood_type": "B+", "allergies": None}
        ]

        patients = []
        for data in patients_data:
            patient = db.query(Patient).filter(Patient.phone == data["phone"]).first()
            if not patient:
                patient = Patient(**data)
                db.add(patient)
                db.commit()
            patients.append(patient)
        print(f"✅ Створено {len(patients)} пацієнтів")

        # 4. Призначення
        print("\n📅 Створення призначень...")
        appointment_statuses = ["scheduled", "confirmed", "completed", "cancelled"]
        appointments = []

        # Беремо існуючих лікарів у базі
        doctors = db.query(User).join(User.roles).filter(Role.name=="Лікар").all()
        if not doctors:
            print("❌ У базі немає лікарів. Додайте лікарів вручну перед seed.")
            return

        for _ in range(20):
            appointment_date = datetime.now().date() + timedelta(days=randint(-7, 30))
            hour = randint(8, 17)
            minute = choice([0, 15, 30, 45])
            appointment_time = time(hour=hour, minute=minute)

            patient = choice(patients)
            doctor = choice(doctors)
            department = None
            if hasattr(doctor, "department"):
                department = doctor.department

            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                department_id=department.id if department else None,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                duration_minutes=choice([15, 30, 45, 60]),
                status=choice(appointment_statuses),
                reason=choice(["Біль у грудях", "Головний біль", "Планова консультація"]),
                notes="Тестове призначення для демонстрації системи",
                created_by_id=doctor.id
            )
            db.add(appointment)
            db.commit()
            appointments.append(appointment)

        print(f"✅ Створено {len(appointments)} призначень")
        print("\n✅ Заповнення тестовими даними завершено!")

    except Exception as e:
        print(f"\n❌ Помилка при заповненні даних: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        seed_test_data()
    except Exception as e:
        print(f"\n❌ Критична помилка: {e}")
        sys.exit(1)
