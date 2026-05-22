from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_, or_
from typing import List
from sqlalchemy.orm import selectinload

from core.database import get_db, hash_password, get_hashed_password
from .models import *
from .shemas import *

router = APIRouter(prefix="/user", tags=['users'])


@router.post("/register", response_model=LoginUser, status_code=201)
async def register_user(data: CreateUser, db: AsyncSession = Depends(get_db)):
    create_passwrod = hash_password(data.password)
    new_user = UserModel(username=data.username,
                         password=create_passwrod)
    db.add(new_user)
    # await db.flush()
    await db.commit()
    await db.refresh(new_user)
    
    # return dict(new_user)
    return new_user
    

@router.post("/info", response_model=ReadUser)
async def info_user(data: SearchUser, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserModel)
        .where(UserModel.id == data.id)
        .options(selectinload(UserModel.players))
        )
    
    user = result.scalar_one_or_none()
    return user



@router.post("/login", response_model=LoginUser)
async def login(data: LogInUser, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserModel)
        .where(UserModel.username == data.username)
        )
    
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=403, detail="Error: 1")
    
    verify_password = get_hashed_password(data.password, user.password)

    if not verify_password:
        raise HTTPException(status_code=403, detail="Error: 2")

    return user

@router.delete("/delete")
async def delete_user(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.id == id)) 
    user = result.scalar_one_or_none()
    await db.delete(user)
    await db.commit()

    return HTTPException(status_code=200, detail="пользователь удален")


@router.put("/update", response_model=ReadUser)
async def update_user(id: int, data:ReadUser, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.id == id)) 
    user = result.scalar_one_or_none()

    user.t_id = data.t_id

    await db.commit()
    await db.refresh(user)

    return user