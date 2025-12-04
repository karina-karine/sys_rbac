from sqlalchemy.orm import Session
from app.models import Role, Permission, User
from app.auth import get_password_hash

def init_rbac_system(db: Session):
    """
    Ініціалізація системи RBAC
    Створює початкові ролі, дозволи та адміністратора
    """
    
    # Перевірка, чи вже ініціалізовано
    if db.query(Role).count() > 0:
        return
    
    # Створення дозволів
    permissions_data = [
        # Користувачі
        ("users.create", "Створення користувачів", "users", "create"),
        ("users.read", "Перегляд користувачів", "users", "read"),
        ("users.update", "Оновлення користувачів", "users", "update"),
        ("users.delete", "Видалення користувачів", "users", "delete"),
        
        # Пацієнти
        ("patients.create", "Додавання пацієнтів", "patients", "create"),
        ("patients.read", "Перегляд пацієнтів", "patients", "read"),
        ("patients.update", "Оновлення даних пацієнтів", "patients", "update"),
        ("patients.delete", "Видалення пацієнтів", "patients", "delete"),
        
        # Записи на прийом
        ("appointments.create", "Створення записів", "appointments", "create"),
        ("appointments.read", "Перегляд записів", "appointments", "read"),
        ("appointments.update", "Оновлення записів", "appointments", "update"),
        ("appointments.delete", "Скасування записів", "appointments", "delete"),
        
        # Медичні записи
        ("medical_records.create", "Створення медичних записів", "medical_records", "create"),
        ("medical_records.read", "Перегляд медичних записів", "medical_records", "read"),
        ("medical_records.update", "Оновлення медичних записів", "medical_records", "update"),
        ("medical_records.delete", "Видалення медичних записів", "medical_records", "delete"),
        
        # Відділення
        ("departments.create", "Створення відділень", "departments", "create"),
        ("departments.read", "Перегляд відділень", "departments", "read"),
        ("departments.update", "Оновлення відділень", "departments", "update"),
        ("departments.delete", "Видалення відділень", "departments", "delete"),
        
        # RBAC
        ("rbac.manage", "Управління ролями та дозволами", "rbac", "manage"),
    ]
    
    permissions = {}
    for name, desc, resource, action in permissions_data:
        perm = Permission(name=name, description=desc, resource=resource, action=action)
        db.add(perm)
        permissions[name] = perm
    
    db.commit()
    
    # Створення ролей
    
    # 1. Адміністратор - повний доступ
    admin_role = Role(
        name="Адміністратор",
        description="Повний доступ до системи",
        priority=100
    )
    admin_role.permissions = list(permissions.values())
    db.add(admin_role)
    
    # 2. Лікар
    doctor_role = Role(
        name="Лікар",
        description="Лікар медичного закладу",
        priority=70
    )
    doctor_role.permissions = [
        permissions["patients.read"],
        permissions["patients.update"],
        permissions["appointments.read"],
        permissions["appointments.update"],
        permissions["medical_records.create"],
        permissions["medical_records.read"],
        permissions["medical_records.update"],
        permissions["departments.read"],
    ]
    db.add(doctor_role)
    
    # 3. Медсестра
    nurse_role = Role(
        name="Медсестра",
        description="Медична сестра",
        priority=50
    )
    nurse_role.permissions = [
        permissions["patients.read"],
        permissions["patients.update"],
        permissions["appointments.read"],
        permissions["appointments.update"],
        permissions["medical_records.read"],
        permissions["departments.read"],
    ]
    db.add(nurse_role)
    
    # 4. Реєстратор
    registrar_role = Role(
        name="Реєстратор",
        description="Співробітник реєстратури",
        priority=40
    )
    registrar_role.permissions = [
        permissions["patients.create"],
        permissions["patients.read"],
        permissions["patients.update"],
        permissions["appointments.create"],
        permissions["appointments.read"],
        permissions["appointments.update"],
        permissions["appointments.delete"],
        permissions["departments.read"],
    ]
    db.add(registrar_role)
    
    # 5. Завідувач відділення
    head_doctor_role = Role(
        name="Завідувач відділення",
        description="Завідувач медичного відділення",
        priority=80
    )
    head_doctor_role.permissions = [
        permissions["patients.read"],
        permissions["patients.update"],
        permissions["appointments.read"],
        permissions["appointments.create"],
        permissions["appointments.update"],
        permissions["appointments.delete"],
        permissions["medical_records.create"],
        permissions["medical_records.read"],
        permissions["medical_records.update"],
        permissions["departments.read"],
        permissions["departments.update"],
        permissions["users.read"],
    ]
    db.add(head_doctor_role)
    
    db.commit()
    
    # Створення адміністратора за замовчуванням
    admin_user = User(
        username="admin",
        email="admin@hospital.ua",
        hashed_password=get_password_hash("admin123"),
        full_name="Системний адміністратор",
        phone="+380501234567",
        is_active=True
    )
    admin_user.roles.append(admin_role)
    db.add(admin_user)
    
    # Створення тестових користувачів
    doctor_user = User(
        username="doctor",
        email="doctor@hospital.ua",
        hashed_password=get_password_hash("doctor123"),
        full_name="Іванов Іван Іванович",
        phone="+380502345678",
        is_active=True
    )
    doctor_user.roles.append(doctor_role)
    db.add(doctor_user)
    
    nurse_user = User(
        username="nurse",
        email="nurse@hospital.ua",
        hashed_password=get_password_hash("nurse123"),
        full_name="Петрова Марія Петрівна",
        phone="+380503456789",
        is_active=True
    )
    nurse_user.roles.append(nurse_role)
    db.add(nurse_user)
    
    registrar_user = User(
        username="registrar",
        email="registrar@hospital.ua",
        hashed_password=get_password_hash("registrar123"),
        full_name="Сидоренко Олена Миколаївна",
        phone="+380504567890",
        is_active=True
    )
    registrar_user.roles.append(registrar_role)
    db.add(registrar_user)
    
    db.commit()
    
    print("✓ Створено ролі та дозволи")
    print("✓ Створено тестових користувачів:")
    print("  - admin/admin123 (Адміністратор)")
    print("  - doctor/doctor123 (Лікар)")
    print("  - nurse/nurse123 (Медсестра)")
    print("  - registrar/registrar123 (Реєстратор)")
