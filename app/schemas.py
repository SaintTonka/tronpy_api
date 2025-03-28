from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AddressInfo(BaseModel):
    address: str
    bandwidth: Optional[int] = Field(default=None)
    energy: Optional[int] = Field(default=None)
    trx_balance: Optional[float] = Field(default=None)

    class Config:
        from_attributes = True

class AddressRequestCreate(BaseModel):
    address: str

class AddressRequestResponse(AddressInfo):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    items: list[AddressRequestResponse]
    total: int
    page: int
    size: int