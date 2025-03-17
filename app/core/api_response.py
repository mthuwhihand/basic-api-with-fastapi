from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi import status


def create_api_response(
    status: int = status.HTTP_200_OK,
    message: str = "Default response",
    # data: Optional[Any] = None,
):
    return JSONResponse(
        status_code=status,
        content={
            "status": status,
            "message": message,
            # "data": (
            #     data
            #     if isinstance(data, (dict, list, str, int, float, bool, type(None)))
            #     else str(data)
            # ),
        },
    )
