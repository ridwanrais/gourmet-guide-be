from pydantic import BaseModel, Field
from typing import Optional


class ErrorDetail(BaseModel):
    message: str = Field(..., example="The requested resource was not found.")
    details: Optional[str] = Field(None, example="User not found.")
    code: Optional[str] = Field(None, example="NF_01")


class ErrorResponse(BaseModel):
    error: ErrorDetail
