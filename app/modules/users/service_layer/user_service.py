from app.modules.users.adapters.repository import UserRepository
from app.shared.security import hash_password


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_all_users(self):
        return self.user_repo.get_all()

    def get_user_by_id(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        return user

    def create_user(self, data):
        existing_user = self.user_repo.get_by_email(data.email)

        if existing_user:
            raise ValueError("Email already registered")

        user_data = {
            "full_name": data.full_name,
            "email": data.email,
            "password_hash": hash_password(data.password),
            "role": "user",
            "status": "active",
        }

        return self.user_repo.create(user_data)

    def update_user(self, user_id: int, data):
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        update_data = {}

        if data.full_name is not None:
            update_data["full_name"] = data.full_name

        if data.email is not None:
            existing_user = self.user_repo.get_by_email(data.email)

            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already used")

            update_data["email"] = data.email

        if data.password is not None:
            update_data["password_hash"] = hash_password(data.password)

        if data.role is not None:
            update_data["role"] = data.role

        if data.status is not None:
            update_data["status"] = data.status

        return self.user_repo.update(user, update_data)

    def delete_user(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        return self.user_repo.delete(user)
