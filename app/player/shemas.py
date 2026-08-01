from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class Hero(BaseModel):
    name: str
    base_hp: int
    base_attack: int
    base_defense: int
    base_agility: int
    base_mana: int
    
    class Config:
        from_attributes=True

class CreateHero(Hero):
    pass


class ChoiceHero(Hero):
    id: int


class ReadHero(Hero):
    id: int
    skills: List["ReadSkills"]
    class Config:
        from_attributes = True

class HeroList(BaseModel):
    heroes: list[ChoiceHero]
    

class Skills(BaseModel):
    name: str
    hero_id: int
    damage_multiplier: float
    base_damage: int
    mana_cost: int
    cooldown: int
    skill_type: str
    description: str 

    class Config:
        from_attributes = True


class ReadSkills(Skills):
    id: int
    # heros: List["HeroModel"]
    # class Config:
    #     from_attributes = True
    

class ChoiceSkill(Skills):
    id: int

class SkillsList(BaseModel):
    skills: list[ChoiceSkill]

    class Config:
        from_attributes = True
    

class Player(BaseModel):
    nickname: str
    user_id: int
    hero_id: int
    


class ReadPlayer(Player):
    id: int
    level: int
    exp: int
    