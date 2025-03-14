from fastapi import Depends, Request, status
from app.core.api_response import APIResponse
from app.core.config import Roles
from app.repositories.user import UserRepository
from app.schemas.users import UserSearchingSchema
from app.utils import extentions


class UserService:
    def __init__(self, user_repo: UserRepository = Depends(UserRepository)):
        self.user_repo = user_repo

    def search(self, request: Request, limit: int = 10, page: int = 1, query: str = ""):
        id = extentions.get_id_from_request(request)
        user = self.user_repo.get_by_id(id)
        if user.role != Roles.ADMIN.value:
            return APIResponse(
                status=status.HTTP_401_UNAUTHORIZED,
                message="You do not have permission to access the resource",
            )
        data = self.user_repo.search(limit, page, query)
        user_schemas = [UserSearchingSchema.model_validate(user) for user in data]

        response = APIResponse(
            status=status.HTTP_200_OK,
            message="Search users successfully!",
            data=user_schemas,
        )

        if page == 1:
            total_records = self.user_repo.get_total_records_of_searching(query)
            response_dict = response.model_dump()
            response_dict["total_records"] = total_records
            return response_dict

        return response
