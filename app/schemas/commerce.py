from pydantic import BaseModel, Field

class RegisterInput(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)
    address: str = Field(min_length=1)

class LoginInput(BaseModel):
    email: str
    password: str

class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    address: str | None = Field(default=None, min_length=1)

class CartAdd(BaseModel):
    item_id: str
    quantity: int = Field(gt=0)

class QuantityUpdate(BaseModel):
    quantity: int = Field(gt=0)
