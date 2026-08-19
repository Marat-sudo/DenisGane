from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from core.database import Base
from typing import List



class PlayerModel(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    hero_id:Mapped[int] = mapped_column(ForeignKey("heros.id"),nullable=False)
    level: Mapped[int] = mapped_column(default=1)
    exp: Mapped[int] = mapped_column(default=0)
    nickname:Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    locations_id:Mapped[int] = mapped_column(ForeignKey("locations.id"),nullable=False)

    mana: Mapped[int] = mapped_column(nullable=False)
    max_mana: Mapped[int] = mapped_column(nullable=False)
    max_hp: Mapped[int] = mapped_column(nullable=False)
    attack: Mapped[int] = mapped_column(nullable=False)
    defense: Mapped[int] = mapped_column(nullable=False)
    agility: Mapped[int] = mapped_column(nullable=False)
    crit_chance: Mapped[float]
    crit_multiplier: Mapped[float]
    
    locations: Mapped["LocationsModel"] = relationship("LocationsModel", back_populates="players")
    users : Mapped[List["UserModel"]] = relationship("UserModel", back_populates="players")
    hero : Mapped[List["HeroModel"]] = relationship("HeroModel", back_populates="players")


class HeroModel(Base):

    __tablename__ ="heros"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str]

    base_hp: Mapped[int] = mapped_column(nullable=False)
    base_attack: Mapped[int] = mapped_column(nullable=False)
    base_defense: Mapped[int] = mapped_column(nullable=False)
    base_agility: Mapped[int] = mapped_column(nullable=False)
    base_mana: Mapped[int] = mapped_column(nullable=False)
    

    skills: Mapped[List["SkillModel"]] = relationship("SkillModel", back_populates="hero")
    players: Mapped[List["PlayerModel"]] = relationship("PlayerModel", back_populates="hero")
    base_crit_chance: Mapped[float] = mapped_column(default=5.0)
    base_crit_multiplier: Mapped[float] = mapped_column(default=1.5)

class SkillModel(Base):

    __tablename__="skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    hero_id:Mapped[int] =mapped_column(ForeignKey("heros.id"),nullable=False)

    level: Mapped[int] = mapped_column(default=1)

    damage_multiplier: Mapped[float]
    base_damage: Mapped[int]
    mana_cost: Mapped[int]
    cooldown: Mapped[int]
    skill_type: Mapped[str]     # ("damage", "heal", "buff", "debuff")
    description: Mapped[str]

    applies_effect_id: Mapped[int | None] = mapped_column(ForeignKey("effecttype.id"), nullable=True)
    effect_duration: Mapped[int | None] = mapped_column(nullable=True)
    effect_chance: Mapped[float | None] = mapped_column(nullable=True)


    hero: Mapped[List["HeroModel"]] = relationship("HeroModel", back_populates="skills")


class PlayerAndSkill(Base):
    __tablename__="playerandskills"
    id: Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    level: Mapped[int] = mapped_column(default=1)






