from sqlalchemy import create_engine, Column, Integer, String  
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData  
from sqlalchemy import create_engine  
from app.player.models import Base, HeroModel, SkillModel
from app.fight.models import FightLog, FightSession
metadata = MetaData()  

# Connect to the database  
engine = create_engine("sqlite:///app.db")  
 
# Drop ONLY the "users" table (targeted deletion)  
# Base.metadata.drop_all(engine, tables=[FightSession.__table__]) 
SkillModel.__table__.drop(engine)

