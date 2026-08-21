from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models import User, UserRole
from app.schemas.schemas import UserOut, UserUpdate
from app.services.notification_service import log_system_action

router = APIRouter()

@router.get("/", response_model=List[UserOut])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN.value]))
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/me", response_model=UserOut)
def update_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_in.email and user_in.email != current_user.email:
        existing = db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
        current_user.email = user_in.email
    if user_in.full_name:
        current_user.full_name = user_in.full_name

    db.commit()
    db.refresh(current_user)
    log_system_action(db=db, user_id=current_user.id, action="User Profile Updated")
    return current_user
