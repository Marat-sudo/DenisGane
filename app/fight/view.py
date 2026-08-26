import random
import tools.db_funs.any_stuff as stf
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.player.models import *
from core.database import get_db
from .models import *
from .shemas import *


router = APIRouter(prefix="/fight")


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

    
    random.shuffle(players)
    opponent = None

    for candidate in players:
        check = await db.execute(
            select(FightSession).where(
                (FightSession.opponent_id == candidate.id) | (FightSession.attacker_id == candidate.id),
                FightSession.status == "active"
            )
        )
        if not check.scalar_one_or_none():
            opponent = candidate
            break

    if not opponent:
        raise HTTPException(status_code=404, detail="Все доступные оппоненты уже находятся в бою")
            
        
    

 
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


@router.get("/history", response_model=ListFights, tags=['fight'])
async def fights_list(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FightModel)
                              .where(
                                    (FightModel.winner_id == id) |
                                    (FightModel.loser_id == id)))
    fights_ = result.scalars().all()

    return ListFights(fights=fights_)


@router.get("/ActiveFight", response_model=choiceActiveFight, tags=['fight'])
async def player_avtive_fight(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FightSession)
                             .where((FightSession.opponent_id == id) |
                                    (FightSession.attacker_id == id),
                                    FightSession.status == "active"))
    fight = result.scalar_one_or_none()

    return fight




@router.post("/effects/create", response_model=ReadEffecType, tags=['effect'])
async def register_hero(data: Effect, db: AsyncSession = Depends(get_db)):
    effect = EffectType(
                        name = data.name,
                        type = data.type,
                        affected_stat = data.affected_stat,
                        modifier_type = data.modifier_type, 
                        modifier_value = data.modifier_value,
                        can_stack = data.can_stack,
                        max_stacks = data.max_stacks
                        )
    

    db.add(effect)
    await db.commit()
    await db.refresh(effect)


    return effect


@router.get("/effects/types", response_model=ListEffects, tags=['effect'])
async def effects_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EffectType))
    effs = result.scalars().all()

    return ListEffects(effects=effs)


@router.get("/effect", response_model=Effect, tags=['effect'])
async def get_effect(eff_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EffectType).where(EffectType.id == eff_id))
    eff = result.scalar_one_or_none()

    return eff


@router.put("/effect/update", tags=['effect'])
async def update_skill(id: int, data: UpdateEffect, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EffectType).where(EffectType.id == id)) 
    effect = result.scalar_one_or_none()

    if not effect:
        raise HTTPException(status_code=404, detail="Не найден эффект")
    
    effect.type = data.type 
    effect.affected_stat = data.affected_stat 
    effect.modifier_type = data.modifier_type 
    effect.modifier_value = data.modifier_value 
    effect.can_stack = data.can_stack 
    effect.max_stacks = data.max_stacks 

    await db.commit()
    await db.refresh(effect)

    raise HTTPException(status_code=200, detail="Запрос обработан")


@router.get("/active-effects", response_model=ListActiveEffect, tags=['effect'])
async def active_effects(session_id: int, player_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActiveEffect)
                              .where(
                                  ActiveEffect.fight_session_id == session_id,
                                  ActiveEffect.target_player_id == player_id,
                                  ActiveEffect.turns_remaining > 0))
    eff = result.scalars().all()

    return ListActiveEffect(effects=eff)


@router.get("/active-effects_by_id", response_model=ListActiveEffect, tags=['effect'])
async def active_effects_with_eff_id(effect_id: int, session_id: int, player_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActiveEffect)
                              .where(
                                  ActiveEffect.fight_session_id == session_id,
                                  ActiveEffect.target_player_id == player_id,
                                  ActiveEffect.effect_type_id == effect_id,
                                  ActiveEffect.turns_remaining > 0))
    eff = result.scalars().all()

    return ListActiveEffect(effects=eff)



@router.get("/active-effects-buff_debuff", response_model=ListEffects, tags=['effect'])
async def active_effects_buff_debuff(session_id: int, player_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActiveEffect)
                              .where(
                                  ActiveEffect.fight_session_id == session_id,
                                  ActiveEffect.target_player_id == player_id))
    eff = result.scalars().all()

    return ListEffects(effects=eff)


@router.put("/updateFightMana", tags=['fight'])
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



@router.post("/step", tags=['fight'])
async def fights_turn(session_id: int, skill_id: int = None, db: AsyncSession = Depends(get_db)):
    async with db.begin():

        result = await db.execute(select(FightSession)
                              .where(
                                    FightSession.id == session_id,
                                    FightSession.status == "active"
                                ))
        session = result.scalar_one_or_none()
    
        if not session:
            raise HTTPException(status_code=404, detail=f"нет данной активной сессии")

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

        if skill_id and not await stf.player_has_skill(attaking_id, skill_id, db):
            raise HTTPException(status_code=404, detail="not player with this skill")

        
        if skillsCooldowns:
            if skill_id:
                for skillcd in skillsCooldowns:
                    if skill_id == skillcd.skill_id and skillcd != 0:
                        # я не помню почему skillcd != 0
                        raise HTTPException(status_code=203, detail="cooldown skill")


            for cd_skill in skillsCooldowns:
                cd_status = (session.attacker_turn and attacker.id == cd_skill.player_id) or (not session.attacker_turn and opponent.id == cd_skill.player_id)
                if cd_status:  
                    cd_skill.turns_remaining -= 1

        if skill_id:
            skill = await stf.get_skill_by_id(skill_id, db)
            
            defen_mana = session.attacker_mana if session.attacker_turn else session.opponent_mana
            if defen_mana < skill.mana_cost:
                    raise HTTPException(status_code=202, detail="недостаточно маны")

            if session.attacker_turn:
                session.attacker_mana -= skill.mana_cost
            else:
                session.opponent_mana -= skill.mana_cost
            
            if skill.applies_effect_id:
                effect_max_stack = await stf.get_effect_stacks(skill.applies_effect_id, db)
                eff_count = await stf.act_eff_id(skill.applies_effect_id, session_id, db)
                if len(eff_count) >= effect_max_stack:
                    raise HTTPException(status_code=203, detail="max effect stacks")
            

                

        # ... получение opponent, attacker и cooldowns ...

        # УБЕРИТЕ промежуточные `await db.commit()` внутри функций step/fight_players!
        # Выполняйте только добавление/обновление объектов через db.add() или изменение полей.

        log = await step(
            session=session, 
            opponent=opponent, 
            attacker=attacker, 
            db=db,
            skill_id=skill_id
        )

        # Если код дошел до конца блока "async with db.begin()",
        # SQLAlchemy сама автоматически выполнит `COMMIT` всех изменений.
        
    return log







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

   


    
@router.get("/session/steps", response_model=ListFightSteps, tags=['fight'])
async def fight_steps_info(fight_id: int, db: AsyncSession = Depends(get_db)):
    """Возвращает все ходы в активном файте"""
    result = await db.execute(select(FightLog)
                              .where(FightLog.fight_session_id == fight_id))
    s = result.scalars().all()

    return ListFightSteps(steps=s)


@router.get("/session/info", response_model=ReadSession, tags=['fight'])
async def fight_session_info(fight_id: int, db: AsyncSession = Depends(get_db)):
    """Возвращает информацию о сесии"""
    result = await db.execute(select(FightSession)
                              .where(FightSession.id == fight_id))
    s = result.scalar_one_or_none()
    return s




@router.get("/cooldown/get", response_model=ReadCooldown, tags=['fight'])
async def cooldowns(session_id: int, player_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerSkillCooldown)
                                        .where(
                                            PlayerSkillCooldown.fight_session_id == session_id,
                                            PlayerSkillCooldown.player_id == player_id
                                            ))
    cooldown = result.scalar_one_or_none()

    return cooldown



    
async def fight_players(attacking, defending, session, db, skill_id=None):
    """Обработка всего и вся"""
    damage = attacking.attack - defending.defense
    final_addition = None
    """
    step_has_dmg - хранит есть ли урон в целом в данном ходу
    когда игрок накладывает бафф/дебафф и не носит урон, комбо не сбрасывается, 
    """
    type_act = "attack"
    spent_mana = 0
    is_crit = False
    crit_dam = 0.0
    effect_applied_id = None
    effect_damage = None

    log_has_dmg = True
    
    dodge_chance = min(50, defending.agility / 2)
          

    effs = await stf.get_active_effects_list(session.id, attacking.id, db)
    
    if effs:
        """проверка наложенных эффектов"""
        effect_damage = 0
        for ActEff in effs: 
            # TODO тут вроде сделал всё, но вроде можно улучшить
            ActEff.turns_remaining -= 1
            

            eff = await stf.get_effect(ActEff.effect_type_id, db)

            mod_value = 0
            if eff.affected_stat == "hp_per_turn":
                if eff.modifier_type == "percent":
                    mod_value = int(attacking.max_hp * (1 + eff.modifier_value / 100)) - attacking.max_hp
                else:
                    mod_value = eff.modifier_value

            elif eff.modifier_type == "percent":
                mod_value = int(getattr(attacking, eff.affected_stat) * (1 + eff.modifier_value / 100))
            elif eff.modifier_type == "flat":
                mod_value = max(getattr(attacking, eff.affected_stat) + eff.modifier_value, 1)


            if eff.affected_stat == "hp_per_turn":
                if session.attacker_turn:
                    session.attacker_current_hp = min(session.attacker_current_hp + mod_value, attacking.max_hp)
                else:        
                    session.opponent_current_hp = min(session.opponent_current_hp + mod_value, attacking.max_hp)
                effect_damage += eff.modifier_value 


    effs = await stf.get_active_effects_list(session.id, attacking.id, db)     
    res = await db.execute(select(SkillModel)
                             .where(SkillModel.id == skill_id))
    skill = res.scalar_one_or_none()

    skill_dmg = skill_id and (skill.skill_type == "buff" or skill.skill_type == "heal")
    if dodge_chance > random.randint(0, 100) and not skill_dmg:
        """проверка на уклонение и создание лога"""
        if session.attacker_turn:
            ahp = session.attacker_current_hp
            dhp = session.opponent_current_hp
            session.attacker_combo=0
        
        else:
            ahp = session.opponent_current_hp
            dhp = session.attacker_current_hp
            session.opponent_combo=0

        log = await stf.createLog(
            attack=attacking, 
            defender=defending, 
            session=session, 
            damage=damage, 
            defHp=dhp,
            attHp=ahp,
            act_type = "dodge",
            skill_id=None,
            mana_spent=spent_mana,
            is_critical=is_crit,
            crit_damage=crit_dam,
            was_dodged=True,
            dodge_chance_rolled=dodge_chance,
            combo_count=0,
            combo_bonus_damage=0,
            effect_applied_id=effect_applied_id,
            effect_damage=effect_damage)

        session.current_turn += 1
        session.attacker_turn = not session.attacker_turn   

        db.add(log)

        return log
        


    if damage <= 0:
        damage = 1

    

    if skill_id:
        type_act = "skill"


        damage, spent_mana, effect_applied_id, log_has_dmg = await stf.skill(session, skill_id, attacking, defending, db)
        
        
        
    
        """
            я понял, чтобы вы денис хотели реализовать, но я решил хранить каждый повторяйщийся
            де/бафф, как новую запись в бд, можно реализовать через stack_count, оно будет работать как надо
            (каждый де\бафф должен иметь не зависимый таймер и применяться одновременно)
            но так сложно преобразовывать данные для пользователя, чтобы было видно каждый эффект
            и сколько ему осталось 

        ╔═══════════════════════════════════╗ 
        ║ Воин                              
        ║ 
        ║ HP: [████████░░] 80/100           
        ║ Атака: 25 → 37 (+50%)             
        ║                                   
        ║ Активные эффекты:                 
        ║ Ярость+50% атаки   (2)  
        ║ Защита +20 защиты   (3)  
        ║ Отравление  -5 HP/ход  (8)
        ╚═══════════════════════════════════╝ -- у вас это было бы 

        ║ Активные эффекты:                 
        ║ Ярость +50% атаки   (2)  
        ║ Защита +20 защиты   (3)  
        ║ Отравление  -5 HP/ход  (1)
        ║ Отравление  -5 HP/ход  (3)
        ║ Отравление  -5 HP/ход  (4)
        ╚═══════════════════════════════════╝ -- как я хотел

        Фактически turns_remaining в вашем случае хранит сколько всего срабатываний 
        произвдет эффект, если не прибавлять к turns_remaining effect_duration, то получается
        что все последующие эффекты перестанут дейвствовать вместе с первым наложенным эффектом такого типа
        https://drive.google.com/file/d/1jWDioC8F9JycjAbxFoSJECEHb9b9cigm/view?usp=sharing
        здесь я расписал как можно реализовать таким методом, он не будет создавать дубликаты в бд
        но будет заменяться applied_at_turn при каждом наложении + Я не смог в адекватной форме это перенести
        в стакающие ДОТы. В теории если в мою формулу включить applied_at_turn и текущий ход,
        то можно привести к виду, который я хотел, но будто проще отдельные логи наложения хранить  
        """

       
    
    if log_has_dmg and attacking.crit_chance >= random.randint(0, 100):
        damage = damage * attacking.crit_multiplier 
        crit_dam = round(damage, 1)
        is_crit = True       


    if session.attacker_turn and session.attacker_combo >= 3 and log_has_dmg:
        damage += damage * (session.attacker_combo - 2) * 0.1

    elif not session.attacker_turn and session.opponent_combo >= 3 and log_has_dmg:
        damage += damage * (session.opponent_combo - 2) * 0.1
    

    defend_hp = session.opponent_current_hp if session.attacker_turn else session.attacker_current_hp
    if log_has_dmg:
        damage = round(damage, 1) 
        newHP = defend_hp - damage 
        newHP = round(newHP, 1)
    else:
        newHP = defend_hp


    if newHP <= 0:
        # TODO сделать снятие де/баффов при выйгрыше
        if session.attacker_turn:
            session.opponent_current_hp = 0.0
        else:
            session.attacker_current_hp = 0.0
        
        session.status = "finish"
        session.winner_id = attacking.id
        newHP = 0.0

        win = FightModel(
                 winner_id=attacking.id,
                 loser_id=defending.id
            )

        db.add(win)
        
        de_ba_ff = await stf.get_active_de_buff(session.id, attacking.id, db)
        if de_ba_ff:
            """снятие баффов / дебаффов"""
            for ActEff in de_ba_ff: 
                eff = await stf.get_effect(ActEff.effect_type_id, db)
                if eff.affected_stat == "hp_per_turn":
                    continue
                mod_value = getattr(attacking, eff.affected_stat) - ActEff.final_addition
                
                setattr(attacking, eff.affected_stat, mod_value)    
        
    if session.attacker_turn:
        session.opponent_current_hp = newHP
        att_hp = session.attacker_current_hp
        
        session.attacker_combo += 1
        comdo = session.attacker_combo
        if session.attacker_combo > session.attacker_max_combo:
            session.attacker_max_combo = session.attacker_combo

    else:
        session.attacker_current_hp = newHP
        att_hp = session.opponent_current_hp
        
        session.opponent_combo += 1
        comdo = session.opponent_combo
        if session.opponent_combo > session.opponent_max_combo:
            session.opponent_max_combo = session.opponent_combo


   
   



    if not log_has_dmg:
        damage = 0
    log = await stf. createLog(
            attack=attacking, 
            defender=defending, 
            session=session, 
            damage=damage, 
            defHp=newHP,
            attHp=att_hp,
            act_type = type_act,
            skill_id=skill_id,
            mana_spent=spent_mana,
            is_critical=is_crit,
            crit_damage=crit_dam,
            was_dodged=False,
            dodge_chance_rolled=dodge_chance,
            combo_count=comdo,
            combo_bonus_damage=(comdo - 2) * 10 if comdo >= 3 else 0,
            effect_applied_id=effect_applied_id,
            effect_damage=effect_damage)
    

    session.current_turn += 1
    session.attacker_turn = not session.attacker_turn

    db.add(log)

    de_ba_ff = await stf.get_active_de_buff_last_step(session.id, attacking.id, db)
    if de_ba_ff:
        """снятие баффов / дебаффов"""
        for ActEff in de_ba_ff: 
            eff = await stf.get_effect(ActEff.effect_type_id, db)
            if eff.affected_stat == "hp_per_turn":
                continue
            mod_value = getattr(attacking, eff.affected_stat) - ActEff.final_addition
            
            setattr(attacking, eff.affected_stat, mod_value)    
   

    return log


    



    
