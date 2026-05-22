from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.player.shemas import ReadPlayer

class User(BaseModel):
    username: str
    

class CreateUser(User):
    password: str
    pass

class ReadUser(User):
    id: int
    t_id: Optional[int] = None
    create_at: datetime
    players : List[ReadPlayer]


class LoginUser(User):
    id: int
    t_id: Optional[int] = None
    
class LogInUser(User):
    username: str
    password: str


class UpdateUser(BaseModel):
    t_id: int

class SearchUser(BaseModel):
    id: int