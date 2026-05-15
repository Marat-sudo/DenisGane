from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from core.database import Base

class LocationsModel(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
     
    name:Mapped[str] = mapped_column(unique=True, nullable=False)
    min_level: Mapped[int] = mapped_column(default=1)
    didescription:Mapped[str] = mapped_column(nullable=False)
    

    
class ProductsModel(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    store_id:Mapped[int] = mapped_column(ForeignKey("store.id"), nullable=False)
    name:Mapped[str] = mapped_column(unique=True, nullable=False)
    didescription:Mapped[str] = mapped_column(nullable=False)
    attributes:Mapped[str] = mapped_column(nullable=False)
    


class StoreModel(Base):
    __tablename__ = "store"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    location_id:Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    name:Mapped[str] = mapped_column(unique=True, nullable=False)
    didescription:Mapped[str] = mapped_column(nullable=False)
    
    

    