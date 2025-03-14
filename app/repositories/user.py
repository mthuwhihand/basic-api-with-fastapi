from fastapi import HTTPException, status
from sqlalchemy import func
from app.models.user import User


class UserRepository:
    def __init__(self, db):
        self.db = db

    def search(self, limit: int = 10, page: int = 1, query: str = ""):
        skip = (page - 1) * limit
        query_lower = query.lower()

        users = (
            self.db.query(User)
            .filter(
                func.lower(User.name).contains(query_lower)
                | func.lower(User.email).contains(query_lower)
            )
            .limit(limit)
            .offset(skip)
            .all()
        )

        return users

    def get_total_records_of_searching(self, query: str = "") -> int:
        total_count = (
            self.db.query(User)
            .filter(User.name.contains(query), User.email.contains(query))
            .count()
        )

        return total_count

    def create(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, id: str, user_dict: dict):
        user = self.get_by_id(id)
        if not user:
            return None

        for key, value in user_dict.items():
            if hasattr(user, key) and key != "id":
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, id: str) -> bool:
        user = self.get_by_id(id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND"
            )

        self.db.delete(user)
        self.db.commit()
        return True

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, id: str) -> User | None:
        return self.db.query(User).filter(User.id == id).first()
