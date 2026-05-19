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


@router.post("/fight/start", tags=['fight'])
async def start_fight(attacker_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == attacker_id)) 
    attacker = result.scalar_one_or_none()
    
    if attacker is None:
        return HTTPException(status_code=404, detail="атакующий не найден")    
    
    result = await db.execute(select(PlayerModel).where(PlayerModel.id != attacker_id))
    players = result.scalars().all()
    opponent = random.choice(players)



    player1 = Fight_player(id = attacker.id, nickname = attacker.nickname, level=attacker.level)
    player2 = Fight_player(id = opponent.id, nickname = opponent.nickname, level=opponent.level)
    
   

    if random.random() < 0.5 : 
        win_player = player1
        loser = player2


    else: 
        
        win_player = player2
        loser = player1

    res = FightModel(winner_id=win_player.id, loser_id=loser.id)
    db.add(res)
    await db.commit()
    await db.refresh(res)

    win = FightResult(fight_id=res.id, 
                        attacker=player1, 
                        opponent=player2, 
                        winner=win_player, 
                        message=f"игрок с уровнем: {win_player.level} {win_player.nickname} победил игрока {loser.nickname} с уровнем {loser.level}")



    return HTTPException(status_code=200, detail=win)