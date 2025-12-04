from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models import User
from app.schemas import Token, UserLogin, UserResponse
from app.auth import (
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Аутентифікація користувача
    
    Повертає JWT токен для доступу до API
    """
    print(f"[DEBUG] Спроба входу користувача: {user_data.username}")
    
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user:
        print(f"[DEBUG] Користувач {user_data.username} не знайдений в БД")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірне ім'я користувача або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"[DEBUG] Користувач знайдений: {user.username}, активний: {user.is_active}")
    print(f"[DEBUG] Хеш паролю в БД: {user.hashed_password[:20]}...")
    
    # Перевірка пароля
    password_valid = verify_password(user_data.password, user.hashed_password)
    print(f"[DEBUG] Перевірка пароля: {password_valid}")
    
    if not password_valid:
        print(f"[DEBUG] Невірний пароль для користувача {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірне ім'я користувача або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        print(f"[DEBUG] Користувач {user_data.username} деактивований")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Обліковий запис деактивовано"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    print(f"[DEBUG] Токен успішно створений для {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Отримання інформації про поточного користувача
    """
    return current_user

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Вихід з системи
    
    Примітка: З JWT токенами вихід реалізується на клієнті шляхом видалення токена
    """
    return {"message": "Успішний вихід з системи"}
