from pydantic import BaseModel

class PropertyBase(BaseModel):
    name: str
    address: str
    price: float

class PropertyCreate(PropertyBase):
    pass

class Property(PropertyBase):
    id: int

    class Config:
        orm_mode = True
