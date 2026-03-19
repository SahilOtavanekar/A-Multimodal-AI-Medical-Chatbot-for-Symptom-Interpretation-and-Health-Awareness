from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None
