from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_, or_
from typing import List

from core.database import get_db
from .models import *
from .shemas import (
    Products,
    CreateLocation,
    ReadLocation,
    CreateStore,
    ReadStore,
    CreateProduct,
    ReadProducts,
    UpdateLocation
)
    



router = APIRouter(prefix="/locations", tags=['locations'])



@router.post("/create", response_model=ReadLocation)
async def register_Locations(data: CreateLocation, db: AsyncSession = Depends(get_db)):
    new_locations = LocationsModel(name=data.name, min_level=data.min_level, didescription=data.didescription)
    db.add(new_locations)
    # await db.flush()
    await db.commit()
    await db.refresh(new_locations)
    
    # return dict(new_user)
    raise HTTPException(status_code=201, detail=dict(data))
    


@router.post("/info", response_model=ReadLocation)
async def info_Locations(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LocationsModel).where(LocationsModel.id == id))
    locations = result.scalar_one_or_none()

    if locations is None:
        raise HTTPException(statuc=404, detail="Location now found")

    return locations


@router.put("/update", response_model=ReadLocation)
async def update_locations(id: int, data:ReadLocation, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LocationsModel).where(LocationsModel.id == id)) 
    locations = result.scalar_one_or_none()

    locations.name = data.name
    locations.min_level = data.min_level
    locations.didescription = data.didescription

    await db.commit()
    await db.refresh(locations)

    return locations

@router.delete("/delete")
async def delete_Locations(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LocationsModel).where(LocationsModel.id == id)) 
    hero = result.scalar_one_or_none()
    await db.delete(hero)
    await db.commit()

    return HTTPException(status_code=200, detail="пользователь удален")




# -----------------------------------------------------------------------

@router.post("/products/create", response_model=ReadProducts)
async def register_products(data: CreateProduct, db: AsyncSession = Depends(get_db)):
    new_products = ProductsModel(name=data.name, didescription=data.didescription, attributes=data.attributes, store_id=data.store_id)
    db.add(new_products)
    # await db.flush()
    await db.commit()
    await db.refresh(new_products)
    
    # return dict(new_user)
    raise HTTPException(status_code=201, detail=dict(data))
    


@router.post("/products/info", response_model=ReadProducts)
async def info_products(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductsModel).where(ProductsModel.id == id))
    locations = result.scalar_one_or_none()


    return locations


@router.put("/products/update", response_model=ReadProducts)
async def update_product(id: int, data:Products, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductsModel).where(ProductsModel.id == id)) 
    products = result.scalar_one_or_none()

    products.name = data.name
    products.didescription = data.didescription
    products.attributes = data.attributes
    products.store_id = data.store_id

    await db.commit()
    await db.refresh(products)

    return products

@router.delete("/products/delete")
async def delete_product(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductsModel).where(ProductsModel.id == id)) 
    products = result.scalar_one_or_none()
    await db.delete(products)
    await db.commit()

    return HTTPException(status_code=200, detail="пользователь удален")

# -------------------------------------------------------------------------------------

@router.post("/store/create", response_model=ReadStore)
async def register_store(data: CreateStore, db: AsyncSession = Depends(get_db)):
    new_store = StoreModel(name=data.name, didescription=data.didescription, location_id=data.location_id)
    db.add(new_store)
    # await db.flush()
    await db.commit()
    await db.refresh(new_store)
    
    # return dict(new_user)
    raise HTTPException(status_code=201, detail=dict(data))
    


@router.post("/store/info", response_model=ReadStore)
async def info_store(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreModel).where(StoreModel.id == id))
    store = result.scalar_one_or_none()


    return store


@router.put("/store/update", response_model=ReadStore)
async def update_store(id: int, data:ReadStore, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreModel).where(StoreModel.id == id)) 
    store = result.scalar_one_or_none()

    store.name = data.name
    store.didescription = data.didescription
    store.location_id = data.location_id

    await db.commit()
    await db.refresh(store)

    return store

@router.delete("/store/delete")
async def delete_store(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreModel).where(StoreModel.id == id)) 
    store = result.scalar_one_or_none()
    await db.delete(store)
    await db.commit()

    return HTTPException(status_code=200, detail="пользователь удален")