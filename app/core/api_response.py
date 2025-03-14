from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    status: int = 500
    message: str = "Default api response"
    data: Optional[Any] = None
