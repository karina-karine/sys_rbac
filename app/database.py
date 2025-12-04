from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Налаштування бази даних SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./hospital_management.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=True  # Логування SQL запитів для дослідження
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency для отримання сесії БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
