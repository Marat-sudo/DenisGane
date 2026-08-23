import random
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.player.models import *
from core.database import get_db
from tools.requests_funs.querys import get_player_skills
from .models import *
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


@router.get("/history", response_model=ListFights)
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




@router.post("/effects/create", response_model=ReadEffecType)
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


@router.get("/effects/types", response_model=ListEffects)
async def effects_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EffectType))
    effs = result.scalars().all()

    return ListEffects(effects=effs)


@router.get("/effect", response_model=Effect)
async def get_effect(eff_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EffectType).where(EffectType.id == eff_id))
    eff = result.scalar_one_or_none()

    return eff

async def get_active_effects_list(session_id: int, player_id: int, db: AsyncSession):
    result = await db.execute(
        select(ActiveEffect).where(
            ActiveEffect.fight_session_id == session_id,
            ActiveEffect.target_player_id == player_id,
            ActiveEffect.turns_remaining > 0
        )
    )
    return result.scalars().all()

@router.get("/active-effects", response_model=ListActiveEffect)
async def active_effects(session_id: int, player_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActiveEffect)
                              .where(
                                  ActiveEffect.fight_session_id == session_id,
                                  ActiveEffect.target_player_id == player_id,
                                  ActiveEffect.turns_remaining > 0))
    eff = result.scalars().all()

    return ListActiveEffect(effects=eff)


@router.get("/active-effects-buff_debuff", response_model=ListEffects)
async def active_effects_buff_debuff(session_id: int, player_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActiveEffect)
                              .where(
                                  ActiveEffect.fight_session_id == session_id,
                                  ActiveEffect.target_player_id == player_id))
    eff = result.scalars().all()

    return ListEffects(effects=eff)


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


# TODO доделать для скилов
@router.post("/step")
async def fights_turn(session_id: int, skill_id: int = None, db: AsyncSession = Depends(get_db)):
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

    if skill_id and not await player_has_skill(attaking_id, skill_id, db):
        raise HTTPException(status_code=404, detail="у данного игрока нет такого скила")

    
    if skillsCooldowns:
        if skill_id:
            for skillcd in skillsCooldowns:
                if skill_id == skillcd.skill_id and skillcd != 0:
                    # я не помню почему skillcd != 0
                    raise HTTPException(status_code=203, detail="не прошло кд навыка")


        for cd_skill in skillsCooldowns:
            cd_status = (session.attacker_turn and attacker.id == cd_skill.player_id) or (not session.attacker_turn and opponent.id == cd_skill.player_id)
            if cd_status:  
                cd_skill.turns_remaining -= 1
                await db.commit()
                await db.refresh(cd_skill)
            
           

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


    return cooldown


async def create_active_effect(effect, session, effect_type_id, attacking_id, defending_id):
    act_eff = ActiveEffect(
        fight_session_id = session.id,
        target_player_id = defending_id,
        caster_player_id = attacking_id,
        effect_type_id = effect_type_id,
        turns_remaining = effect.current_turn,
        stack_count = 0,
        applied_at_turn = session.id
    )

    return act_eff


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
        damage: float,
        defHp: float,
        attHp: float,
        act_type: str,
        skill_id: int,
        mana_spent: int,
        is_critical: bool,
        crit_damage: float,
        was_dodged: bool,
        dodge_chance_rolled: float,
        combo_count: int,
        combo_bonus_damage: int,
        effect_applied_id: int,
        effect_damage: float) -> FightLog:
    

    if is_critical:
        descript = f"{attack.nickname} ({attHp} HP) нанёс {defender.nickname} {damage} крит урона, понизив хп провивника до {defHp} HP"
    
    elif was_dodged:
        descript = f"{defender.nickname} {defHp} уклонился от атаки {attack.nickname} {attHp} и не получил урон HP"
    
    elif skill_id:
        

        descript =f"{attack.nickname} ({attHp} HP) нет {defender.nickname} {damage}, понизив хп провивника до {defHp} HP"
    
    elif effect_applied_id and effect_applied_id < 0:
        descript = f"{attack.nickname} ({attHp} HP) попытался наложить эффект на игрока {defender.nickname} ({defHp} HP), но не получилось"
    
    elif effect_applied_id and damage > 0:
        descript = f"{attack.nickname} ({attHp} HP) нанёс игроку {damage} урона {defender.nickname} ({defHp} HP), и наложил эффект"

    elif effect_applied_id:
        descript = f"{attack.nickname} ({attHp} HP) наложил эффект на игрока {defender.nickname} ({defHp} HP)"

    else:     
        descript = f"{attack.nickname} ({attHp} HP) нанёс {defender.nickname} {damage} урона, понизив хп провивника до {defHp} HP"
    
    _log = FightLog(
        fight_session_id = session.id,
        turn_number = session.current_turn,
        attacker_id = attack.id, 
        defender_id = defender.id,
        damage_dealt = damage,

        action_type = act_type,
        description = descript,
        skill_id = skill_id,
        mana_spent = mana_spent,
        is_critical = is_critical,
        crit_damage=crit_damage,

        was_dodged=was_dodged,
        dodge_chance_rolled=dodge_chance_rolled,
        combo_count=combo_count,
        combo_bonus_damage=combo_bonus_damage,
        effect_applied_id=effect_applied_id,
        effect_damage=effect_damage)
    return _log

    
async def fight_players(attacking, defending, session, db, skill_id=None):
    """Обработка всего и вся"""
    damage = attacking.attack - defending.defense
    step_has_dmg = True 
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

    effs = await get_active_effects_list(session.id, attacking.id, db)
    
    if effs:
        """проверка наложенных эффектов"""
        effect_damage = 0
        for ActEff in effs: 
            # TODO тут вроде сделал всё, но вроде можно улучшить
            ActEff.turns_remaining -= 1
            

            eff = await get_effect(ActEff.effect_type_id, db)

            mod_value = 0
            if eff.affected_stat == "hp_per_turn":
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

            
            

    if dodge_chance > random.randint(0, 100):
        """проверка на уклонение и создание лога"""
        if session.attacker_turn:
            ahp = session.attacker_current_hp
            dhp = session.opponent_current_hp
            session.attacker_combo=0
        
        else:
            ahp = session.opponent_current_hp
            dhp = session.attacker_current_hp
            session.opponent_combo=0

        log = await createLog(attack=attacking, 
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
        await db.commit()
        await db.refresh(session)
        await db.refresh(log) 

        return log
        


    if damage <= 0:
        damage = 1

    defen_mana = session.attacker_mana if session.attacker_turn else session.opponent_mana

    if skill_id:
        """Обработка использования скила / наложение эффекта"""
        res = await db.execute(select(SkillModel)
                             .where(SkillModel.id == skill_id))
        skill = res.scalar_one_or_none()

        if defen_mana < skill.mana_cost:
                raise HTTPException(status_code=202, detail="недостаточно маны")

        if session.attacker_turn:
            session.attacker_mana -= skill.mana_cost
        else:
            session.opponent_mana -= skill.mana_cost

        type_act = "skill"
        spent_mana = skill.mana_cost

        cd = await create_cooldown(
                session_id=session.id, 
                player_id=attacking.id, 
                skill_id=skill.id,
                _cooldown=skill.cooldown,
                db=db)
        
        # db.add(cd)
        # await db.commit()
        
        if skill.damage_multiplier == 0.0:
            log_has_dmg = True

        else:
            damage = (attacking.attack * skill.damage_multiplier + skill.base_damage) - defending.defense       

        if skill.effect_chance > random.randint(0, 1):
            
            eff = await get_effect(skill.applies_effect_id, db)

            if eff.modifier_type == "percent" and eff.affected_stat != "hp_per_turn":
                mod_value = int(getattr(attacking, eff.affected_stat) * (1 + eff.modifier_value / 100))
            elif eff.affected_stat != "hp_per_turn":
                mod_value = max(getattr(attacking, eff.affected_stat) + eff.modifier_value, 1)

            if skill.skill_type == "buff":
                setattr(attacking, eff.affected_stat, mod_value)    
                    
            elif skill.skill_type == "debuff" and eff.affected_stat != "hp_per_turn":
                setattr(defending, eff.affected_stat, mod_value)  
            
            act_eff = ActiveEffect(
                fight_session_id = session.id,
                target_player_id = defending.id,
                caster_player_id = attacking.id,
                effect_type_id = eff.id,
                turns_remaining = skill.effect_duration,
                applied_at_turn = session.current_turn
                )
            
            db.add(act_eff)
        
        else:
            """Если не получилось наложить эффект его айди становиться отрицательным"""
            effect_applied_id = skill.applies_effect_id * -1
        
    
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
        crit_dam = round(damage, 2)
        is_crit = True       


    if session.attacker_turn and session.attacker_combo >= 3:
        damage += damage * (session.attacker_combo - 2) * 0.1

    elif not session.attacker_turn and session.opponent_combo >= 3:
        damage += damage * (session.opponent_combo - 2) * 0.1
    

    defend_hp = session.opponent_current_hp if session.attacker_turn else session.attacker_current_hp
    if log_has_dmg:
        damage = round(damage, 2) 
        newHP = defend_hp - damage 
        newHP = round(newHP, 2)
    else:
        newHP = defend_hp


    if newHP <= 0:

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


    log = await createLog(attack=attacking, 
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
            
        

            
    

    de_ba_ff = await get_active_effects_list(session.id, attacking.id, db)

    if de_ba_ff:
        """снятие баффов / дебаффов"""
        for ActEff in de_ba_ff: 
            eff = await get_effect(ActEff.effect_type_id, db)
            if eff.affected_stat == "hp_per_turn":
                continue

            mod_value = getattr(attacking, eff.affected_stat) - ActEff.final_addition
            if eff.type == "buff":
                setattr(attacking, eff.affected_stat, mod_value)    
                    
            elif eff.type == "debuff":
                setattr(attacking, eff.affected_stat, mod_value) 
                
            
        
        await db.refresh(attacking)
            
    

    session.current_turn += 1
    session.attacker_turn = not session.attacker_turn

    db.add(log)
    await db.commit()
    await db.refresh(session)
    await db.refresh(log)
    await db.refresh(attacking)
    await db.refresh(defending) 

    return log


    



    
