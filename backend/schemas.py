from pydantic import BaseModel

class PropertyBase(BaseModel):
    name: str
    address: str
    price: float

class PropertyCreate(PropertyBase):
    pass

class Property(BaseModel):
    id: int
    name: str
    address: str
    price: float

    class Config:
        from_attributes = True
