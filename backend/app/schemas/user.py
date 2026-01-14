from pydantic import BaseModel, Field

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(UserBase):
    password: str

class User(UserBase):
    id: str
    
    class Config:
        from_attributes = True
