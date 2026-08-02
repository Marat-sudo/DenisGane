from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_, or_
from typing import List
from sqlalchemy.orm import selectinload
import random

from core.database import get_db
from .models import *
from app.player.models import *
from app.player.shemas import Skills
from .shemas import *

router = APIRouter(prefix="/fight", tags=['fight'])


@router.post("/start", tags=['fight'])
async def start_fight(attacker_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == attacker_id)) 
    attacker = result.scalar_one_or_none()
    check_attaker = await db.execute(select(FightSession)
                                     .where(
                                            (FightSession.attacker_id == attacker.id) |
                                            (FightSession.opponent_id == attacker.id),
                                            FightSession.status =="active"))
    if check_attaker.scalar_one_or_none():
        raise HTTPException(status_code=200, detail="вы уже находитесь в бою")
    
    result = await db.execute(select(PlayerModel)
                              .where(PlayerModel.id != attacker_id))
    players = result.scalars().all()

    if not players:
         raise HTTPException(status_code=404, detail="оппоненты не найдены")

    async def chech_status_opponent():
        opponent = random.choice(players)
        check = await db.execute(select(FightSession)
                             .where((FightSession.opponent_id == opponent.id) |
                                    (FightSession.attacker_id == opponent.id),
                                    FightSession.status == "active"))
    
      
        result_check = check.scalar_one_or_none()
        print(result_check)
        print(players)
        if result_check:
            players.pop(opponent)
            if len(players) <= 0:
                  return False
            return await chech_status_opponent()
        else:
            return opponent
        
        
    opponent = await chech_status_opponent()

 
    session = FightSession(
        attacker_id = attacker.id,
        opponent_id = opponent.id,
        attacker_current_hp = attacker.max_hp,
        opponent_current_hp = opponent.max_hp,
        attacker_mana = attacker.mana,
        opponent_mana = opponent.mana
    )


    db.add(session)
    await db.commit()
    await db.refresh(session)

    
    return HTTPException(status_code=200, detail=session)


@router.post("/history", response_model=ListFights)
async def fights_list(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FightModel)
                              .where(
                                    (FightModel.winner_id == id) |
                                    (FightModel.loser_id == id)))
    fights_ = result.scalars().all()

    return ListFights(fights=fights_)



@router.post("/fight/step")
async def fights_turn(session_id: int, skill_id: int = None, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FightSession)
                              .where(FightSession.id == session_id))
    session = result.scalar_one_or_none()


    res = await db.execute(select(PlayerModel)
                              .where(PlayerModel.id == session.opponent_id))
    opponent = res.scalar_one_or_none()

    res = await db.execute(select(PlayerModel)
                              .where(PlayerModel.id == session.attacker_id))
    attacker  = res.scalar_one_or_none()

    res = await db.execute(select(PlayerSkillCooldown)
                .where(
                    PlayerSkillCooldown.fight_session_id == session_id,
                    (PlayerSkillCooldown.player_id == attacker.id) |
                    (PlayerSkillCooldown.player_id == opponent.id)
                    ))
    skillsCooldowns = res.scalars().all()
    print("-" * 100)
    print(skillsCooldowns)
    

    return await step(
                    session=session, 
                    opponent=opponent, 
                    attacker=attacker, 
                    db=db,
                    skill_id=skill_id)

async def player_has_skill(player_id, skill_id):
    res = await db.execute(select(PlayerAndSkill)
                            .where(
                                player_id=player_id,
                                skill_id=skill_id
                            ))
    has = res.scalar_one_or_none()
    print(has)
    print("a" * 100)
    return has

async def step(session, opponent, attacker, db, skill_id=None):
    damage = 0
    type_act = "attack"
    spent_mana = 0

    attaking_id = attacker.id if session.attacker_turn else opponent.id
    
    if skill_id and not player_has_skill(attaking_id, skill_id):
        raise HTTPException(status_code=404, detail="у данного игрока нет такого скила")

    if session.attacker_turn:
        if skill_id:
            res = await db.execute(select(SkillModel)
                                .where(SkillModel.id == skill_id))
            skill = res.scalar_one_or_none()
            if skill.skill_type == "damage":
                damage = (attacker.attack * skill.damage_multiplier + skill.base_damage) - opponent.defense       
                attacker.mana -= skill.mana_cost
                type_act = "skill"
                spent_mana = skill.mana_cost

                await create_cooldown(
                    session_id=session.id, 
                    player_id=attacker.id, 
                    skill_id=skill.id,
                    _cooldown=skill.cooldown,
                    db=db)

        else:
            damage = attacker.attack - opponent.defense
                

        if damage < 0:
                damage = 1
            
        newHP = session.opponent_current_hp - damage

        if newHP <= 0:
            session.opponent_current_hp = 0
            session.status = "finish"
            session.winner_id = attacker.id
            newHP = 0

            win = FightModel(
                 winner_id=attacker.id,
                 loser_id=opponent.id
            )

            db.add(win)
            await db.commit()
            await db.refresh(session)
            
            return win


        session.opponent_current_hp = newHP
        log = await createLog(attack=attacker, 
                        defender=opponent, 
                        session=session, 
                        damage=damage, 
                        defHp=newHP,
                        attHp=session.attacker_current_hp,                            
                        act_type=type_act,
                        skill_id=skill_id,
                        mana_spent=spent_mana,
                        is_critical=False)
    
    
    # атакует оппонент
    else:
        if skill_id:
            res = await db.execute(select(SkillModel)
                                .where(SkillModel.id == skill_id))
            skill = res.scalar_one_or_none()

            if skill.skill_type == "damage":
                damage = (opponent.attack * skill.damage_multiplier + skill.base_damage) - attacker.defense       
                opponent.mana -= skill.mana_cost
                type_act = "skill"
                spent_mana = skill.mana_cost

                await create_cooldown(
                    session_id=session.id, 
                    player_id=opponent.id, 
                    skill_id=skill.id,
                    _cooldown=skill.cooldown,
                    db=db)
            
        else:
            damage = opponent.attack - attacker.defense
              

        if damage < 0:
                damage = 1
            
        newHP = session.attacker_current_hp - damage

        if newHP <= 0:
            session.attacker_current_hp = 0

            session.status = "finish"
            session.winner_id = opponent.id
            newHP = 0

            win = FightModel(
                 winner_id=opponent.id,
                 loser_id=attacker.id
            )

            db.add(win)
            await db.commit()
            await db.refresh(session)
            
            return win
            


        session.attacker_current_hp = newHP
        log = await createLog(attack=opponent, 
                        defender=attacker, 
                        session=session, 
                        damage=damage, 
                        defHp=newHP,
                        attHp=session.opponent_current_hp,
                        act_type = type_act,
                        skill_id=skill_id,
                        mana_spent=spent_mana,
                        is_critical=False)
            
        

            
    session.current_turn += 1
    session.attacker_turn = not session.attacker_turn   

    db.add(log)
    await db.commit()
    await db.refresh(session)
    await db.refresh(log) 

    return log



    
@router.post("/session", response_model=ListFightSteps)
async def fight_steps_info(fight_id: int, db: AsyncSession = Depends(get_db)):
    """Возвращает все ходы в активном файте"""
    result = await db.execute(select(FightLog)
                              .where(FightLog.fight_session_id == fight_id))
    s = result.scalars().all()

    return ListFightSteps(steps=s)

# @router.post("/cooldown/create", response_model=ReadCooldown)
async def create_cooldown(session_id: int, player_id: int, skill_id: int, _cooldown: int, db: AsyncSession):
    cooldown = PlayerSkillCooldown(
            fight_session_id=session_id,
            player_id=player_id,
            skill_id=skill_id,
            turns_remaining =_cooldown
    )
    db.add(cooldown)
    await db.commit()
    await db.refresh(cooldown)

    return cooldown


@router.get("/cooldown/get", response_model=ReadCooldown)
async def cooldowns(session_id: int, player_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerSkillCooldown)
                                        .where(
                                            PlayerSkillCooldown.fight_session_id == session_id,
                                            PlayerSkillCooldown.player_id == player_id
                                            ))
    cooldown = result.scalar_one_or_none()

    return cooldown

async def createLog(
        attack: PlayerModel, 
        defender: PlayerModel,
        session: FightSession,
        damage: int,
        defHp: int,
        attHp: int,
        act_type: str,
        skill_id: int,
        mana_spent: int,
        is_critical: bool) -> FightLog:
    
    _log = FightLog(
        fight_session_id = session.id,
        turn_number = session.current_turn,
        attacker_id = attack.id, 
        defender_id = defender.id,
        damage_dealt = damage,

        action_type = act_type,
        description = f"{attack.nickname} ({attHp} HP) нанёс {defender.nickname} {damage} урона до {defHp} HP",
        
        skill_id = skill_id,
        mana_spent = mana_spent,
        is_critical = is_critical
        )
    return _log

    



    



    
