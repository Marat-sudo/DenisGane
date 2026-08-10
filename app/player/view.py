from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.locations.models import LocationsModel
from core.database import get_db

from .models import *
from .shemas import *

router = APIRouter(prefix="/player", tags=['player'])


@router.post("/hero/create", response_model=ReadHero, tags=['hero'])
async def register_hero(data: Hero, db: AsyncSession = Depends(get_db)):
    new_hero = HeroModel(name=data.name, 
                         base_hp = data.base_hp, 
                         base_attack = data.base_attack, 
                         base_defense = data.base_defense,
                         base_agility = data.base_agility,
                         base_mana = data.base_mana)
    db.add(new_hero)
    # await db.flush()
    await db.commit()
    await db.refresh(new_hero)
    result = await db.execute(select(HeroModel)
                              .where(HeroModel.id == new_hero.id)
                              .options(selectinload(HeroModel.skills)))
    hero = result.scalar_one_or_none()
    # return dict(new_user)
    return hero
    


@router.get("/hero/info", response_model=ReadHero, tags=['hero'] )
async def info_hero(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HeroModel)
                                        .where(HeroModel.id == id)
                                        .options(selectinload(HeroModel.skills)))
    hero = result.scalar_one_or_none()

    return hero


@router.get("/hero/list",  response_model=HeroList, tags=['hero'])
async def hero_list(db: AsyncSession = Depends(get_db)):
    # SELECT id, name FROM heros;
    result = await db.execute(select(HeroModel))
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

    new_skill = SkillModel(name=data.name, 
                           hero_id = data.hero_id,
                           damage_multiplier = data.damage_multiplier,
                           base_damage = data.base_damage,
                           mana_cost = data.mana_cost,
                           cooldown = data.cooldown,
                           skill_type = data.skill_type,
                           description = data.description
                           )

    db.add(new_skill)
    # await db.flush()
    await db.commit()
    await db.refresh(new_skill)
    
    return new_skill
    

@router.get("/skills", response_model=SkillsList)
async def player_skills(id: int, db: AsyncSession = Depends(get_db)):
    """Возвращает скилы пользователя"""
    result = await db.execute(select(SkillModel).where(SkillModel.hero_id == id))
    _skills = result.scalars().all()

    return SkillsList(skills=_skills)


@router.delete("/skills/delete", tags=['skills'])
async def delete_skill(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SkillModel).where(SkillModel.id == id)) 
    skill = result.scalar_one_or_none()
    await db.delete(skill)
    await db.commit()

    return HTTPException(status_code=200, detail="пользователь удален")




@router.post("/create", response_model=ReadPlayer, status_code=201)
async def register_Player(data: Player, db: AsyncSession = Depends(get_db)):

    min_loc = await db.execute(select(LocationsModel)
                              .where(LocationsModel.min_level == 0))

    loc = min_loc.scalar_one_or_none()

    result = await db.execute(select(HeroModel)
                              .where(HeroModel.id == data.hero_id))
    
    hero = result.scalar_one_or_none()
    print(hero)
    # INSERT INTO player (nickname, hero_id, user_id)
    #VALUES ("илья", 2, 4)
    new_player = PlayerModel(
        nickname=data.nickname, 
        hero_id=data.hero_id, 
        user_id=data.user_id,
        locations_id = loc.id,
        max_hp = hero.base_hp,
        attack = hero.base_attack,
        defense = hero.base_defense,
        agility = hero.base_agility,
        mana = hero.base_mana,
        max_mana = hero.base_mana,
        crit_chance= hero.base_crit_chance,
        crit_multiplier=hero.base_crit_multiplier)
    


    db.add(new_player)
    await db.commit()
    await db.refresh(new_player)

    
    # SELECT id, name, skills, players FROM heros WHERE id == 3 
    result = await db.execute(select(HeroModel)
                              .where(HeroModel.id == data.hero_id)
                              .options(selectinload(HeroModel.skills)))
    hero = result.scalar_one_or_none()

    for skill in hero.skills:
        # INSERT INTO playerandskills (player_id, skill_id)
        # VALUES (1, 2)

        new_ps = PlayerAndSkill(player_id = new_player.id, skill_id = skill.id)
        db.add(new_ps)
        await db.commit()
        await db.refresh(new_ps)


    return new_player

@router.put("/update", response_model=ReadPlayer)
async def update_player(id: int, data: UpdatePlayer, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == id)) 
    player = result.scalar_one_or_none()

     

    player.max_hp = data.base_hp
    player.attack = data.base_attack
    player.defense = data.base_defense
    player.agility = data.base_agility
    player.mana = data.base_mana
    player.max_mana = data.base_mana
    player.crit_chance= data.base_crit_chance
    player.crit_multiplier=data.base_crit_multiplier

    await db.commit()
    await db.refresh(player)

    return player


@router.put("/setSkill", response_model=ReadPlayerSkill, status_code=201)
async def set_player_skill(player_id: int, skill_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(PlayerModel)
                            .where(PlayerModel.id == player_id))
    player = res.scalar_one_or_none()

    res = await db.execute(select(SkillModel)
                            .where(
                                SkillModel.id == skill_id,
                                SkillModel.hero_id == player.hero_id
                            ))
    skill = res.scalar_one_or_none()

    if not skill:
        raise HTTPException(status_code=404, detail="нет такой зависимости")



    skill_player = PlayerAndSkill(
            player_id=player.id,
            skill_id = skill.id
    )

    db.add(skill_player)
    await db.commit()
    await db.refresh(skill_player)

    return skill_player
    

@router.put("/updateMana", response_model=ReadPlayer)
async def update_location(id: int, mana: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == id)) 
    player = result.scalar_one_or_none()

    player.mana = mana

    await db.commit()
    await db.refresh(player)

    return player
    
@router.put("/updatePlayerLocation", response_model=ReadPlayer)
async def update_player_loc(id: int, loc_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == id)) 
    player = result.scalar_one_or_none()

    player.locations_id = loc_id

    await db.commit()
    await db.refresh(player)

    return player


@router.get("/info", response_model=ReadPlayer)
async def info_player(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == id))
    player = result.scalar_one_or_none()

    return player


@router.get("/combat-stats", response_model=StatsPlayer)
async def stats_player(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == id))
    player = result.scalar_one_or_none()

   
    dodge_chance = min(50, player.agility / 2)

    player.dodge_chance = dodge_chance

    stats = StatsPlayer.model_validate(player, from_attributes=True)

    return stats
