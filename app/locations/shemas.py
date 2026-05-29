from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional,List


class LocationsBase(BaseModel):
    name: str
    min_level: int
    didescription: str
    class Config:
        from_attributes=True


class LocationList(BaseModel):
    locations: List[ReadLocation]
    

class Products(BaseModel):
    store_id: int
    name: str
    didescription: str
    attributes: str

class StoreBase(BaseModel):
    name: str
    didescription: str
    location_id: int

class ReadLocations(LocationsBase):
    id: int


class ReadProducts(Products):
    id: int

class ReadStore(StoreBase):
    id: int

class CreateLocation(LocationsBase):
    pass

class UpdateLocation(LocationsBase):
    pass

class ReadLocation(LocationsBase):
    id: int
    pass

class CreateProduct(LocationsBase):
    pass


class CreateStore(LocationsBase):
    pass




