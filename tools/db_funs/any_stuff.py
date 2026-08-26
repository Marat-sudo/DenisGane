import random
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.player.models import *
from core.database import get_db
from app.fight.models import *



async def get_active_effects_list(session_id: int, player_id: int, db: AsyncSession):
    result = await db.execute(
        select(ActiveEffect).where(
            ActiveEffect.fight_session_id == session_id,
            ActiveEffect.target_player_id == player_id,
            ActiveEffect.turns_remaining > 0
        )
    )
    return result.scalars().all()

async def get_active_de_buff_last_step(session_id: int, player_id: int, db: AsyncSession):
    result = await db.execute(
        select(ActiveEffect).where(
            ActiveEffect.fight_session_id == session_id,
            ActiveEffect.final_addition != None,
            ActiveEffect.target_player_id == player_id,
            ActiveEffect.turns_remaining == 1
        )
    )
    return result.scalars().all()


async def get_active_de_buff(session_id: int, player_id: int, db: AsyncSession):
    result = await db.execute(
        select(ActiveEffect).where(
            ActiveEffect.fight_session_id == session_id,
            ActiveEffect.final_addition != None,
            ActiveEffect.target_player_id == player_id,
            ActiveEffect.turns_remaining > 0 
        )
    )
    return result.scalars().all()


async def player_has_skill(player_id, skill_id, db):
    res = await db.execute(select(PlayerAndSkill)
                            .where(
                                PlayerAndSkill.player_id == player_id,
                                PlayerAndSkill.skill_id ==skill_id
                            ))
    has = res.scalar_one_or_none()
    return has


async def act_eff_id(eff_id: int, session_id: int, db:AsyncSession) -> list:
    res = await db.execute(select(ActiveEffect)
                            .where(
                                ActiveEffect.effect_type_id == eff_id,
                                ActiveEffect.fight_session_id== session_id))
    
    return res.scalars().all()

async def get_skill_by_id(skill_id: int, db:AsyncSession):
    res = await db.execute(select(SkillModel)
                            .where(
                                SkillModel.id == skill_id))
    
    return res.scalar_one_or_none()


async def get_effect_stacks(eff_id: int, db:AsyncSession) -> int:
    res = await db.execute(select(EffectType.max_stacks)
                            .where(EffectType.id == eff_id))
    
    return res.scalar_one_or_none()


async def get_effect(eff_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EffectType).where(EffectType.id == eff_id))
    eff = result.scalar_one_or_none()
    if not eff:
            raise HTTPException(status_code=404, detail="не нашлось ничего")
    
    return eff





async def skill(session, skill_id, attacking, defending, db):
    damage = attacking.attack - defending.defense
    final_addition = None
    spent_mana = 0
    effect_applied_id = None
    log_has_dmg = True

    skill = await get_skill_by_id(skill_id, db)
    """Обработка использования скила / наложение эффекта"""

    

    
    spent_mana = skill.mana_cost

    cooldown = PlayerSkillCooldown(
        fight_session_id=session.id,
        player_id=attacking.id,
        skill_id=skill_id,
        turns_remaining = skill.cooldown)
    
    db.add(cooldown)
    
    if skill.skill_type == "heal":
        if session.attacker_turn:
            session.attacker_current_hp = min(session.attacker_current_hp + skill.base_damage, attacking.max_hp)
        
        else:
            session.opponent_current_hp = min(session.opponent_current_hp + skill.base_damage, defending.max_hp)


    if skill.damage_multiplier == 0.0:
        log_has_dmg = False

    else:
        damage = (attacking.attack * skill.damage_multiplier + skill.base_damage) - defending.defense       

    if skill.effect_chance and skill.effect_chance > random.randint(0, 1):
        
        eff = await get_effect(skill.applies_effect_id, db)
        person = attacking if skill.skill_type == "buff" else defending

        if eff.affected_stat == "hp_per_turn":
           pass
        
        elif eff.modifier_type == "percent":
            
            mod_value = int(getattr(person, eff.affected_stat) * (1 + eff.modifier_value / 100))
        
        
        elif eff.modifier_type == "flat":
            mod_value = max(getattr(person, eff.affected_stat) + eff.modifier_value, 1)
        


        if eff.affected_stat == "hp_per_turn":
            pass
        
        elif skill.skill_type == "buff":
            final_addition = mod_value - getattr(attacking, eff.affected_stat) 
            setattr(attacking, eff.affected_stat, mod_value)
            db.add(attacking)
            
                  
        elif skill.skill_type == "debuff":
            final_addition = mod_value - getattr(defending, eff.affected_stat)
            setattr(defending, eff.affected_stat, mod_value)  
            db.add(defending)

        act_eff = ActiveEffect(
            fight_session_id = session.id,
            target_player_id = attacking.id if eff.type == "buff" or eff.type == "heal" else defending.id,
            caster_player_id = attacking.id,
            effect_type_id = eff.id,
            turns_remaining = skill.effect_duration,
            final_addition = final_addition,
            applied_at_turn = session.current_turn
            )
        
        db.add(act_eff)

        effect_applied_id = skill.applies_effect_id

    elif skill.effect_chance:
        """Если не получилось наложить эффект его айди становиться отрицательным"""
        effect_applied_id = skill.applies_effect_id * -1
    
    return damage, spent_mana, effect_applied_id, log_has_dmg










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