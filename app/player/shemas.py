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

    base_crit_chance: float
    base_crit_multiplier: float
    
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
    

class SkillCooldown(BaseModel):
    id: int
    cooldown: int

    class Config:
        from_attributes = True

class Skills(BaseModel):
    """skill_type: str - тип навыка ("damage", "heal", "buff", "debuff") """
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
    
class Update_player_mana(BaseModel):
    mana: int


class ReadPlayer(Player):
    id: int
    locations_id: int
    level: int
    exp: int
    mana: int
    max_mana: int
    max_hp: int
    attack: int
    defense: int
    agility: int
    crit_chance: float
    crit_multiplier: float
    

class UpdatePlayer(BaseModel):
    nickname: str
    base_hp: int 
    base_attack: int
    base_defense: int
    base_agility: int
    base_mana: int
    base_crit_chance: float
    base_crit_multiplier: float


class ReadPlayerSkill(BaseModel):
    id: int
    player_id: int
    skill_id: int
    level: int