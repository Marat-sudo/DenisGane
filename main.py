from fastapi import FastAPI
from core.database import engine, Base

from app.user.models import *
from app.player.models import *

from app.user.view import router as user_router
from app.player.view import router as player_router
from app.locations.view import router as locations_router

app = FastAPI(
    title="game"
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("таблицы успешно созданы")

app.include_router(user_router)

app.include_router(player_router)

app.include_router(locations_router)
