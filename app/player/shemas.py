from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class Hero(BaseModel):
    name: str
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
        orm_mode = True

class HeroList(BaseModel):
    heroes: list[ChoiceHero]
    

class Skills(BaseModel):
    hero_id: int
    name: str

class ReadSkills(Skills):
    id: int

class Player(BaseModel):
    nickname: str
    user_id: int
    hero_id: int

class ReadPlayer(Player):
    id: int
    level: int
    exp: int