from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash
from typing import Optional, List


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_all(self, search: str = "", skip: int = 0, limit: int = 100) -> List[User]:
        query = self.db.query(User)
        if search:
            query = query.filter(
                (User.name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
            )
        return query.offset(skip).limit(limit).all()

    def create(self, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            password=hashed_password,
            role=user_data.role,
            title=user_data.title,
            isAdmin=user_data.isAdmin,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True

    def change_password(self, user_id: int, new_password: str) -> Optional[User]:
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.password = get_password_hash(new_password)
        self.db.commit()
        self.db.refresh(user)
        return user
