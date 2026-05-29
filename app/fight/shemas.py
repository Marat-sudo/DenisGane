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



