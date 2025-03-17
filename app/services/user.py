import math
from fastapi import Request, status
from sqlalchemy import func
from sqlalchemy.orm import load_only
from app.core.api_response import create_api_response
from app.core.config import AccountStatuses, Roles
from app.models.users import User
from app.schemas.users import UserSearchingSchema
from app.utils import extentions
from app.core.database import db


def search(request: Request, limit: int = 10, page: int = 1, query: str = ""):
    id = extentions.get_id_from_request(request)

    user = (
        db.query(User)
        .filter_by(id=id)
        .filter(User.status == AccountStatuses.ACTIVE.value)
        .first()
    )
    if user.role != Roles.ADMIN.value:
        return create_api_response(
            status=status.HTTP_403_FORBIDDEN,
            message="You do not have permission to access the resource",
        )

    skip = (page - 1) * limit
    query_lower = query.lower()

    data = (
        db.query(User)
        .options(
            load_only(
                User.id,
                User.name,
                User.email,
                User.role,
                User.phone,
                User.address,
                User.dob,
                User.status,
            )
        )
        .filter(
            func.lower(User.name).contains(query_lower)
            | func.lower(User.email).contains(query_lower)
        )
        .limit(limit)
        .offset(skip)
        .all()
    )

    total_records = (
        db.query(func.count(User.id))
        .filter(
            func.lower(User.name).contains(query_lower)
            | func.lower(User.email).contains(query_lower)
        )
        .scalar()
    )

    user_schemas = [UserSearchingSchema.model_validate(user) for user in data]

    return {
        "status": status.HTTP_200_OK,
        "message": "Searching users successfully!",
        "data": user_schemas,
        "total_records": total_records,
        "current_page": page,
        "total_pages": math.ceil(total_records / limit),
    }
