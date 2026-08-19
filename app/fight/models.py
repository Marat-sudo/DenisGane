from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class FightModel(Base):
    __tablename__ = "fights"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fight: Mapped[datetime] = mapped_column(default=datetime.now)

    winner_id:Mapped[int] = mapped_column(ForeignKey("players.id"),nullable=False)
    loser_id:Mapped[int] = mapped_column(ForeignKey("players.id"),nullable=False)

   
class FightSession(Base):
    __tablename__ = "fightsession"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    attacker_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    opponent_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)

    attacker_current_hp: Mapped[float] = mapped_column(nullable=False)
    opponent_current_hp: Mapped[float] = mapped_column(nullable=False)
    attacker_mana: Mapped[int]
    opponent_mana: Mapped[int]

    winner_id: Mapped[int] = mapped_column(nullable=True, default=None)

    current_turn: Mapped[int] = mapped_column(default=1)
    attacker_turn: Mapped[bool] = mapped_column(default=True)

    status: Mapped[str] = mapped_column(default="active")

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    attacker_combo: Mapped[int] = mapped_column(default=0)
    opponent_combo: Mapped[int] = mapped_column(default=0)
    attacker_max_combo: Mapped[int] = mapped_column(default=0)
    opponent_max_combo: Mapped[int] = mapped_column(default=0)


   
class FightLog(Base):
    __tablename__ = "fightlog"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    fight_session_id: Mapped[int] = mapped_column(ForeignKey("fightsession.id"),nullable=False)

    turn_number: Mapped[int]
    attacker_id: Mapped[int]
    defender_id: Mapped[int]
    damage_dealt: Mapped[float]

    action_type: Mapped[str]
    description: Mapped[str]

    skill_id: Mapped[int] = mapped_column(nullable=True)
    mana_spent: Mapped[int]
    is_critical: Mapped[bool]
    crit_damage: Mapped[float]

    was_dodged: Mapped[bool]
    dodge_chance_rolled: Mapped[float]

    combo_count: Mapped[int]  
    combo_bonus_damage: Mapped[int]   # хранит число в процентах (10%)

    effect_applied_id: Mapped[int] = mapped_column(ForeignKey("effecttype.id"), nullable=True)
    effect_damage: Mapped[int] = mapped_column(nullable=True) 


    
class PlayerSkillCooldown(Base):
    __tablename__="playerskillcooldown"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fight_session_id: Mapped[int] = mapped_column(ForeignKey("fightsession.id"),nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"),nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"),nullable=False)
    turns_remaining: Mapped[int]


class EffectType(Base):
    __tablename__ = "effecttype"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]  
    type: Mapped[str] 
    affected_stat: Mapped[str]   # ("attack", "defense", "agility", "hp_per_turn")
    modifier_type: Mapped[str]   # ("percent", "flat") 
    modifier_value: Mapped[float] 
    can_stack: Mapped[bool] 
    max_stacks: Mapped[int] 




class ActiveEffect(Base):
    __tablename__ = "activeeffect"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fight_session_id: Mapped[int] = mapped_column(ForeignKey("fightsession.id"),nullable=False)
    target_player_id: Mapped[int]
    caster_player_id: Mapped[int]
    effect_type_id: Mapped[int] = mapped_column(ForeignKey("effecttype.id"),nullable=False)
    turns_remaining: Mapped[int]
    applied_at_turn: Mapped[int]
