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


@router.get("/ActiveFight", response_model=choiceActiveFight)
async def player_avtive_fight(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FightSession)
                             .where((FightSession.opponent_id == id) |
                                    (FightSession.attacker_id == id),
                                    FightSession.status == "active"))
    fight = result.scalar_one_or_none()

    return fight


@router.put("/updateFightMana")
async def update_mana_in_fight(session_id: int, player_id: int,mana: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FightSession)
                        .where(
                            FightSession.id == session_id,
                            (FightSession.attacker_id == player_id) |
                            (FightSession.opponent_id == player_id)
                            ))

    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="не верный айди сессии или игрока в сесии")

    if session.attacker_id == player_id:
        session.attacker_mana = mana
    else:
        session.opponent_mana = mana

    await db.commit()
    await db.refresh(session)

    raise HTTPException(status_code=200, detail=f"мана пополнена до {mana}")


@router.post("/step")
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
                    PlayerSkillCooldown.turns_remaining > 0,
                    (PlayerSkillCooldown.player_id == attacker.id) |
                    (PlayerSkillCooldown.player_id == opponent.id)
                    ))

    skillsCooldowns = res.scalars().all()
    

    attaking_id = attacker.id if session.attacker_turn else opponent.id

    if skill_id and not await player_has_skill(attaking_id, skill_id, db):
        raise HTTPException(status_code=404, detail="у данного игрока нет такого скила")

    
    if skillsCooldowns:
        for skillcd in skillsCooldowns:
            if skill_id and skill_id == skillcd.skill_id and skillcd != 0:
                raise HTTPException(status_code=203, detail="не прошло кд навыка")

        for cd_skill in skillsCooldowns:
            if session.attacker_turn and attacker.id == cd_skill.player_id:
                skillcd.turns_remaining -= 1
                await db.commit()
                await db.refresh(skillcd)
            
            elif not session.attacker_turn and opponent.id == cd_skill.player_id:
                skillcd.turns_remaining -= 1
                await db.commit()
                await db.refresh(skillcd)

    return await step(
                    session=session, 
                    opponent=opponent, 
                    attacker=attacker, 
                    db=db,
                    skill_id=skill_id)

async def player_has_skill(player_id, skill_id, db):
    res = await db.execute(select(PlayerAndSkill)
                            .where(
                                PlayerAndSkill.player_id == player_id,
                                PlayerAndSkill.skill_id ==skill_id
                            ))
    has = res.scalar_one_or_none()
    return has

async def step(session, opponent, attacker, db, skill_id=None):
    

   
    
    if session.attacker_turn:
        return await fight_players(
            attacking=attacker,
            defending=opponent,
            session=session,
            db=db,
            skill_id=skill_id
        )
    else:
        return await fight_players(
            attacking=opponent,
            defending=attacker,
            session=session,
            db=db,
            skill_id=skill_id
        )

   

    
@router.get("/session/steps", response_model=ListFightSteps)
async def fight_steps_info(fight_id: int, db: AsyncSession = Depends(get_db)):
    """Возвращает все ходы в активном файте"""
    result = await db.execute(select(FightLog)
                              .where(FightLog.fight_session_id == fight_id))
    s = result.scalars().all()

    return ListFightSteps(steps=s)

@router.get("/session/info", response_model=ReadSession)
async def fight_session_info(fight_id: int, db: AsyncSession = Depends(get_db)):
    """Возвращает информацию о сесии"""
    result = await db.execute(select(FightSession)
                              .where(FightSession.id == fight_id))
    s = result.scalar_one_or_none()
    return s


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

    
async def fight_players(attacking, defending, session, db, skill_id=None):
    """Обработка всего и вся"""
    damage = 0
    type_act = "attack"
    spent_mana = 0

    defen_mana = session.attacker_mana if session.attacker_turn else session.opponent_mana

    if skill_id:
        res = await db.execute(select(SkillModel)
                             .where(SkillModel.id == skill_id))
        skill = res.scalar_one_or_none()

        if defen_mana< skill.mana_cost:
                raise HTTPException(status_code=202, detail="недостаточно маны")

        if skill.skill_type == "damage":
            damage = (attacking.attack * skill.damage_multiplier + skill.base_damage) - defending.defense       
            if session.attacker_turn:
                session.attacker_mana -= skill.mana_cost
            else:
                session.opponent_mana -= skill.mana_cost
        
            
            type_act = "skill"
            spent_mana = skill.mana_cost

            await create_cooldown(
                    session_id=session.id, 
                    player_id=attacking.id, 
                    skill_id=skill.id,
                    _cooldown=skill.cooldown,
                    db=db)
            
    else:
        damage = attacking.attack - defending.defense
              

    if damage < 0:
        damage = 1
    

    defend_hp = session.opponent_current_hp if session.attacker_turn else session.attacker_current_hp 
    newHP = defend_hp - damage 

    if newHP <= 0:

        if session.attacker_turn:
            session.opponent_current_hp = 0
        else:
            session.attacker_current_hp = 0
        
        session.status = "finish"
        session.winner_id = attacking.id
        newHP = 0

        win = FightModel(
                 winner_id=attacking.id,
                 loser_id=defending.id
            )

        db.add(win)
        await db.commit()
        await db.refresh(session)
        await db.refresh(attacking)
        await db.refresh(defending)
            
        return win
            

    if session.attacker_turn:
        session.opponent_current_hp = newHP
        att_hp = session.attacker_current_hp
    else:
        session.attacker_current_hp = newHP
        att_hp = session.opponent_current_hp
        
    log = await createLog(attack=attacking, 
                        defender=defending, 
                        session=session, 
                        damage=damage, 
                        defHp=newHP,
                        attHp=att_hp,
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


    



    
