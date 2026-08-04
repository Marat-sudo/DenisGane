from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from core.database import Base
from sqlalchemy import ForeignKey
from typing import List

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


   
class FightLog(Base):
    __tablename__ = "fightlog"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    fight_session_id: Mapped[int] = mapped_column(ForeignKey("fightsession.id"),nullable=False)

    turn_number: Mapped[int]
    attacker_id: Mapped[int]
    defender_id: Mapped[int]
    damage_dealt: Mapped[int]

    action_type: Mapped[str]
    description: Mapped[str]

    skill_id: Mapped[int] = mapped_column(nullable=True)
    mana_spent: Mapped[int]
    is_critical: Mapped[bool]


    
class PlayerSkillCooldown(Base):
    __tablename__="playerskillcooldown"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fight_session_id: Mapped[int] = mapped_column(ForeignKey("fightsession.id"),nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"),nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"),nullable=False)
    turns_remaining: Mapped[int]


