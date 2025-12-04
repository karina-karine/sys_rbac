"""
Скрипт для повного скидання та пересоздання бази даних

ВИКОРИСТАННЯ:
1. Зупиніть сервер (Ctrl+C)
2. Запустіть: python reset_database.py
3. Знову запустіть сервер: python -m app.main
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import SQLALCHEMY_DATABASE_URL, Base
from app.rbac import init_rbac_system

def reset_database():
    """Повне скидання бази даних"""
    
    db_file = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
    
    # Видаляємо існуючу базу даних
    if os.path.exists(db_file):
        os.remove(db_file)
        print("✓ Видалено стару базу даних")
    
    # Створюємо нову базу даних
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
    Base.metadata.create_all(bind=engine)
    print("✓ Створено нову базу даних")
    
    # Ініціалізуємо RBAC систему
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        init_rbac_system(db)
        print("✓ RBAC систему ініціалізовано")
        print("\n✅ База даних успішно скинута!")
        print("\nТестові користувачі:")
        print("  - admin/admin123 (Адміністратор)")
        print("  - doctor/doctor123 (Лікар)")
        print("  - nurse/nurse123 (Медсестра)")
        print("  - registrar/registrar123 (Реєстратор)")
    finally:
        db.close()

if __name__ == "__main__":
    print("⚠️  УВАГА: Це видалить всі дані з бази!")
    answer = input("Продовжити? (yes/no): ")
    
    if answer.lower() in ["yes", "y", "так", "т"]:
        reset_database()
    else:
        print("Скасовано")
