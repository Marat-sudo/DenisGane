from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.player.shemas import ReadPlayer

class Fight_player(BaseModel):
    id: int
    nickname: str
    level: int


class FightResult(BaseModel):
    fight_id: int
    attacker: Fight_player
    opponent: Fight_player
    winner: Fight_player
    message: str

    class Config:
        from_attributes=True


class choiceFight(BaseModel):
    id: int 
    fight: datetime
    winner_id: int
    loser_id: int
    
class ReadFight(choiceFight):
    id: int
    class Config:
        from_attributes = True


class ListFights(BaseModel):
    fights: List[ReadFight]

    class Config:
        from_attributes = True



class choiceFightStep(BaseModel):
    id: int 
    fight_session_id: int
    turn_number: int
    attacker_id: int
    defender_id: int
    damage_dealt: int

    action_type: str
    description: str

    class Config:
        from_attributes = True
    
class ReadFightStep(choiceFightStep):
    id: int


class ListFightSteps(BaseModel):
    steps: List[ReadFightStep]







