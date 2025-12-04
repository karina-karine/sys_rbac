from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Role, Permission
from app.schemas import RoleResponse, RolePermissionsResponse, PermissionResponse
from app.auth import get_current_user, require_permission

router = APIRouter()

@router.get("/roles", response_model=List[RolePermissionsResponse])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac.manage"))
):
    """Отримання всіх ролей з їх дозволами"""
    roles = db.query(Role).all()
    return roles

@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac.manage"))
):
    """Отримання всіх дозволів"""
    permissions = db.query(Permission).all()
    return permissions

@router.get("/my-permissions", response_model=List[PermissionResponse])
async def get_my_permissions(
    current_user: User = Depends(get_current_user)
):
    """Отримання дозволів поточного користувача"""
    all_permissions = []
    for role in current_user.roles:
        all_permissions.extend(role.permissions)
    
    # Унікальні дозволи
    unique_permissions = list({perm.id: perm for perm in all_permissions}.values())
    return unique_permissions

@router.post("/roles/{role_id}/permissions/{permission_id}")
async def assign_permission_to_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac.manage"))
):
    """Призначення дозволу ролі"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Роль не знайдено")
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Дозвіл не знайдено")
    
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.commit()
    
    return {"message": f"Дозвіл '{permission.name}' додано до ролі '{role.name}'"}

@router.delete("/roles/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("rbac.manage"))
):
    """Видалення дозволу у ролі"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Роль не знайдено")
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Дозвіл не знайдено")
    
    if permission in role.permissions:
        role.permissions.remove(permission)
        db.commit()
    
    return {"message": f"Дозвіл '{permission.name}' видалено з ролі '{role.name}'"}
