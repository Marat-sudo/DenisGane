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


# class ReadTurn()

class ListFights(BaseModel):
    fights: List[ReadFight]

    class Config:
        from_attributes = True


class choiceActiveFight(BaseModel):
    id: int



class choiceFightStep(BaseModel):
    id: int 
    fight_session_id: int
    turn_number: int
    attacker_id: int
    defender_id: int
    damage_dealt: float

    action_type: str
    description: str

    class Config:
        from_attributes = True
    
class ReadFightStep(choiceFightStep):
    id: int


class ListFightSteps(BaseModel):
    steps: List[ReadFightStep]


class Cooldown(BaseModel):
    id: int
    fight_session_id: int
    player_id: int
    skill_id: int
    turns_remaining: int

    class Config:
        from_attributes = True


class ReadSession(BaseModel):
    id: int
    attacker_id: int
    opponent_id: int
    attacker_current_hp: float
    opponent_current_hp: float
    attacker_mana: int
    opponent_mana: int

    winner_id: Optional[int] = None

    current_turn: int
    attacker_turn: bool

    status: str
    created_at: datetime

class ReadCooldown(Cooldown):
    id: int

    class Config:
        from_attributes = True
    







