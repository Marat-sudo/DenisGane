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

async def get_active_effects_last_step(session_id: int, player_id: int, db: AsyncSession):
    result = await db.execute(
        select(ActiveEffect).where(
            ActiveEffect.fight_session_id == session_id,
            (ActiveEffect.target_player_id == player_id),
            ActiveEffect.turns_remaining == 1
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