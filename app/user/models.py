from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from core.database import Base
from typing import List

class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    t_id: Mapped[int | None] = mapped_column(unique=True, nullable=True)

    #password
    create_at: Mapped[datetime] = mapped_column(default=datetime.now)

    players : Mapped[List["PlayerModel"]] = relationship("PlayerModel", back_populates="users")

