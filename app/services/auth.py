from fastapi import Depends, Request, status
from app.core.api_response import APIResponse
from app.models.user import User
from app.schemas.users import SignUp, SignIn, UserSchema, UserUpdateSchema
from app.repositories.user import UserRepository
from app.utils import extentions
from app.core.config import Roles


class AuthService:
    def __init__(self, user_repo: UserRepository = Depends(UserRepository)):
        self.user_repo = user_repo

    def register(self, user_data: SignUp):
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            return APIResponse(
                status=status.HTTP_401_UNAUTHORIZED, message="Email aldeady registered"
            )

        new_user = User(**user_data.model_dump())
        new_user.id = extentions.gen_uuid()
        new_user.password = extentions.hash_password(new_user.password)
        new_user.role = Roles.USER.value
        new_user.refresh_token = extentions.create_refresh_token({"id": new_user.id})
        new_user = self.user_repo.create(new_user)

        new_access_token = extentions.create_access_token({"id": new_user.id})
        data = UserSchema.model_validate(new_user)
        data.access_token = new_access_token
        return APIResponse(
            status=status.HTTP_200_OK, message="Register successfully", data=data
        )

    def log_in(self, sign_in_data: SignIn):
        existing_user = self.user_repo.get_by_email(sign_in_data.email)
        if existing_user:
            existing_user.refresh_token = extentions.create_refresh_token(
                {"id": existing_user.id}
            )
            if not extentions.is_valid_password(
                sign_in_data.password, existing_user.password
            ):
                return APIResponse(
                    status=status.HTTP_401_UNAUTHORIZED, message="Invalid password"
                )

            new_access_token = extentions.create_access_token({"id": existing_user.id})
            data = UserSchema.model_validate(existing_user)
            data.access_token = new_access_token
            return APIResponse(
                status=status.HTTP_200_OK, message="Login successfully", data=data
            )
        else:
            return APIResponse(status=status.HTTP_404_NOT_FOUND, message="Not found")

    def refresh_access_token(self, request: Request):
        id = extentions.get_id_from_request(request)
        new_access_token = extentions.create_access_token({"id": id})
        return APIResponse(
            status=status.HTTP_200_OK,
            message="Refresh access token successfully!",
            data={"token": new_access_token},
        )

    def log_out(self, request: Request):
        id = extentions.get_id_from_request(request)
        updated = self.user_repo.update(id, {"refresh_token": None})
        if not updated:
            return APIResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Logout failed"
            )
        return APIResponse(
            status=status.HTTP_200_OK, message="Logged out successfully!"
        )

    def update_name(self, request: Request, data: UserUpdateSchema):
        id = extentions.get_id_from_request(request)
        update_data = data.model_dump(exclude_unset=True)  # Chỉ lấy giá trị có dữ liệu

        if not update_data:
            return APIResponse(
                status=status.HTTP_400_BAD_REQUEST, message="No data to update!"
            )

        updated_user = self.user_repo.update(id, update_data)
        data = UserSchema.model_validate(updated_user)
        return APIResponse(
            status=status.HTTP_200_OK, message="Update info successful!", data=data
        )

    def change_password(self, request: Request, current_pass: str, new_pass: str):
        id = extentions.get_id_from_request(request)

        current_user = self.user_repo.get_by_id(id)
        if current_user:
            if not extentions.is_valid_password(current_pass, current_user.password):
                return APIResponse(
                    status=status.HTTP_401_UNAUTHORIZED, message="Invalid password"
                )
            else:
                current_user.password = extentions.hash_password(new_pass)
                current_user = self.user_repo.update(
                    id, {"password": current_user.password}
                )
                data = UserSchema.model_validate(current_user)
                return APIResponse(
                    status=status.HTTP_200_OK,
                    message="Change password successful!",
                    data=data,
                )
        else:
            return APIResponse(status=status.HTTP_404_NOT_FOUND, message="Not found")

    def delete(self, request: Request, target_id: str):
        id = extentions.get_id_from_request(request)
        user = self.user_repo.get_by_id(id)

        if id != target_id:  # If user wanna delete user having target_id
            if (
                user.role == Roles.ADMIN.value
            ):  # Check role, have permission if role admin
                if self.user_repo.delete(id):
                    return APIResponse(
                        status=status.HTTP_200_OK,
                        message="Delete account successfully!",
                    )
                return APIResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Delete account failed! Something went wrong at BE service",
                )

            return APIResponse(
                status=status.HTTP_401_UNAUTHORIZED,
                message="You do not have permission to delete this account!",
            )
        else:  # User wanna delete him/herself
            if (
                user.role != Roles.ADMIN.value
            ):  # Check role, have permission if it is not role admin
                if self.user_repo.delete(id):  # Because admin can not delete themselves
                    return APIResponse(
                        status=status.HTTP_200_OK,
                        message="Delete account successfully!",
                    )

                return APIResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Delete account failed! Something went wrong at BE service",
                )

            return APIResponse(
                status=status.HTTP_401_UNAUTHORIZED,
                message="Your account are admin account, Can not delete admin account!",
            )
