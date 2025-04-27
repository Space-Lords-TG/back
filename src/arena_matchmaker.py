from telegram import Bot
import os
from src.infrastructure.database import SessionLocal
from src.application.arena_service import ArenaService
# import time
import asyncio

async def run_arena_matchmaking(bot, interval: int = 5):
    while True:
        db = SessionLocal()
        try:
            arena = ArenaService(db)
            matches = arena.find_match()
            if not matches:
                print("[DEBUG] Нет подходящих матчей")
            for p1, p2 in matches:
                result = arena.resolve_battle(p1, p2)
                if result is None:
                    continue
                await arena.notify_players_about_fight(p1, p2, result, bot)
                print(f"[BATTLE] {result['result'].upper()} - {p1} vs {p2}")
        except Exception as e:
            print("Error during matchmaking:", str(e))
        finally:
            db.close()
        await asyncio.sleep(interval)