from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    SECRET_KEY: str = "SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 9999
    
    class Config:
        env_file = ".env"

settings = Settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo = True,
    connect_args={"check_same_thread" : False}
)

AsyncSessionLocal = async_sessionmaker( 
    bind=engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session