from datetime import datetime
from sqlalchemy.orm import Session
from app.modules.users.adapters.orm import UserORM


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return (
            self.db.query(UserORM)
            .filter(UserORM.deleted_at.is_(None))
            .order_by(UserORM.id.desc())
            .all()
        )

    def get_by_id(self, user_id: int):
        return (
            self.db.query(UserORM)
            .filter(UserORM.id == user_id, UserORM.deleted_at.is_(None))
            .first()
        )

    def get_by_email(self, email: str):
        return (
            self.db.query(UserORM)
            .filter(UserORM.email == email, UserORM.deleted_at.is_(None))
            .first()
        )

    def create(self, data: dict):
        user = UserORM(**data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: UserORM, data: dict):
        for key, value in data.items():
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: UserORM):
        user.deleted_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
