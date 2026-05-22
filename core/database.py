from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from pydantic_settings import BaseSettings
import hashlib, os

def hash_password(password: str) -> str:
    salt = os.urandom(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("UTF-8"),
        salt,
        10000
    )

    return f"{salt.hex()}${hashed.hex()}"

def get_hashed_password(hash_password: str, passwrod: str) -> bool:
    try:
        salt_hex, hash_hex = passwrod.split("$")
        salt = bytes.fromhex(salt_hex)

        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            hash_password.encode("UTF-8"),
            salt,
            10000
        )
        return hashed.hex() == hash_hex
    except:
        return False


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