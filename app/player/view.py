from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_, or_
from typing import List
from sqlalchemy.orm import selectinload

from core.database import get_db
from .models import *
from .shemas import *

router = APIRouter(prefix="/player", tags=['player'])


@router.post("/hero/create", response_model=ReadHero, tags=['hero'])
async def register_hero(data: Hero, db: AsyncSession = Depends(get_db)):
    new_hero = HeroModel(name=data.name)
    db.add(new_hero)
    # await db.flush()
    await db.commit()
    await db.refresh(new_hero)
    
    # return dict(new_user)
    raise HTTPException(status_code=201, detail=dict(data))
    


@router.post("/hero/info", response_model=ReadHero, tags=['hero'] )
async def info_hero(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HeroModel).where(HeroModel.id == id))
    hero = result.scalar_one_or_none()

    return hero


@router.post("/hero/list", response_model=HeroList, tags=["hero"])
async def hero_list(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HeroModel).where())
    heroes = result.scalars().all()

    return HeroList(heroes=heroes)


@router.delete("/hero/delete", tags=['hero'])
async def delete_hero(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HeroModel).where(HeroModel.id == id)) 
    hero = result.scalar_one_or_none()
    await db.delete(hero)
    await db.commit()

    return HTTPException(status_code=200, detail="пользователь удален")




@router.post("/skills/create", response_model=ReadSkills, tags=['skills'])
async def register_skill(data: Skills, db: AsyncSession = Depends(get_db)):

    new_skill = SkillModel(name=data.name, hero_id = data.hero_id)
    db.add(new_skill)
    # await db.flush()
    await db.commit()
    await db.refresh(new_skill)
    
    # return dict(new_user)
    raise HTTPException(status_code=201, detail=dict(data))
    


@router.delete("/skills/delete", tags=['skills'])
async def delete_skill(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SkillModel).where(SkillModel.id == id)) 
    skill = result.scalar_one_or_none()
    await db.delete(skill)
    await db.commit()

    return HTTPException(status_code=200, detail="пользователь удален")




@router.post("/create", response_model=ReadPlayer)
async def register_Player(data: Player, db: AsyncSession = Depends(get_db)):

    new_player = PlayerModel(
        nickname=data.nickname, 
        hero_id=data.hero_id, 
        user_id=data.user_id)
    
    db.add(new_player)
    await db.commit()
    await db.refresh(new_player)
    
    result = await db.execute(select(HeroModel).where(HeroModel.id == new_player.hero_id).options(selectinload(HeroModel.skills)))
    hero = result.scalar_one_or_none()

    for skill in hero.skills:
        new_ps = playerAndSkill(player_id = new_player.id, skill_id = skill.id)
        db.add(new_ps)
        await db.commit()


    return new_player


@router.post("/info", response_model=ReadPlayer)
async def info_player(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == id))
    player = result.scalar('user_or_none')

    return player