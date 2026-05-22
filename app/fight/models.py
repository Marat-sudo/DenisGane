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

   
