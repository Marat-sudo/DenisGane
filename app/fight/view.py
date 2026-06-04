from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_, or_
from typing import List
from sqlalchemy.orm import selectinload
import random

from core.database import get_db
from .models import *
from app.player.models import *

from .shemas import *

router = APIRouter(prefix="/fight", tags=['fight'])


@router.post("/start", tags=['fight'])
async def start_fight(attacker_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == attacker_id)) 
    attacker = result.scalar_one_or_none()
    
    if attacker is None:
        return HTTPException(status_code=404, detail="атакующий не найден")    
    
    result = await db.execute(select(PlayerModel)
                              .where(PlayerModel.id != attacker_id))
    players = result.scalars().all()
    opponent = random.choice(players)


    session = FightSession(
        attacker_id = attacker.id,
        opponent_id = opponent.id,
        attacker_current_hp = attacker.max_hp,
        opponent_current_hp = opponent.max_hp
    )


    db.add(session)
    await db.commit()
    await db.refresh(session)

    
    return HTTPException(status_code=200, detail=session)


@router.post("/userList", response_model=ListFights)
async def fights_list(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FightModel)
                              .where(
                                    (FightModel.winner_id == id) |
                                    (FightModel.loser_id == id)))
    fights_ = result.scalars().all()

    return ListFights(fights=fights_)


@router.post("/playerHasFight", response_model=ListFights)
async def player_Has_Fight(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FightModel)
                              .where(
                                    (FightModel.winner_id == id) |
                                    (FightModel.loser_id == id)))
    fights_ = result.scalars().all()

    return ListFights(fights=fights_)



@router.post("/startFight")
async def fights_turn(session_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FightSession)
                              .where(FightSession.id == session_id))
    session = result.scalar_one_or_none()


    res = await db.execute(select(PlayerModel)
                              .where(PlayerModel.id == session.opponent_id))
    opponent = res.scalar_one_or_none()

    res = await db.execute(select(PlayerModel)
                              .where(PlayerModel.id == session.attacker_id))
    attacker  = res.scalar_one_or_none()

    if session.attacker_turn:
        damage = attacker.attack - opponent.defense

        if damage < 0:
                damage = 1
            
        newHP = session.opponent_current_hp - damage

        if newHP <= 0:
            session.opponent_current_hp = 0
            session.status = "finish"
            session.winner_id = attacker.id


        else:
            session.opponent_current_hp = newHP

            

            log = createLog(attacker, 
                            opponent, 
                            session, 
                            damage, 
                            newHP,
                            session.attacker_current_hp)
       
            session.current_turn += 1
            session.attacker_turn = not session.attacker_turn
        

    # атакует оппонент
    else:
        

        damage = opponent.attack - attacker.defense

        if damage < 0:
                damage = 1
            
        newHP = session.attacker_current_hp - damage

        if newHP <= 0:
            session.attacker_current_hp = 0

            session.status = "finish"
            session.winner_id = opponent.id

        else:

            session.attacker_current_hp = newHP

            log = createLog(opponent, 
                            attacker, 
                            session, 
                            damage, 
                            newHP, 
                            session.opponent_current_hp)
            
            session.current_turn += 1
            session.attacker_turn = not session.attacker_turn

    db.add(log)
    await db.commit()
    await db.refresh(session)
    await db.refresh(log)

    return log



@router.post("/steps/next", response_model=ListFightSteps)
async def fight_steps_info(fight_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FightLog)
                              .where(FightLog.fight_session_id == fight_id))
    s = result.scalars().all()

    print(s)

    return ListFightSteps(steps=s)

    
@router.post("/steps/info", response_model=ListFightSteps)
async def fight_steps_info(fight_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FightLog)
                              .where(FightLog.fight_session_id == fight_id))
    s = result.scalars().all()

    print(s)

    return ListFightSteps(steps=s)





def createLog(
        attack: PlayerModel, 
        defender: PlayerModel,
        session: FightSession,
        damage: int,
        defHp: int,
        attHp: int) -> FightLog:
    
    _log = FightLog(
        fight_session_id = session.id,
        turn_number = session.current_turn,
        attacker_id = attack.id, 
        defender_id = defender.id,
        damage_dealt = damage,

        action_type = "attack",
        description = f"{attack.nickname} ({attHp} HP) нанёс {defender.nickname} {damage} урона до {defHp} HP"
        )
    return _log

    



    



    
