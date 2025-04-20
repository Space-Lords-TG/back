from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from datetime import datetime, timezone
from src.infrastructure.models import ArenaQueue, Ship, ArenaFight
from src.application.ship_service import ShipService
from telegram import Bot
from telegram.constants import ParseMode
import asyncio

class ArenaService:
    def __init__(self, db: Session):
        self.db = db
        self.ship_service = ShipService(db)

    def is_in_queue(self, player_id: int) -> bool:
        return self.db.get(ArenaQueue, player_id) is not None

    def join_queue(self, player_id: int):
        if not self.is_in_queue(player_id):
            entry = ArenaQueue(player_id=player_id)
            self.db.add(entry)
            self.db.commit()

    def leave_queue(self, player_id: int):
        self.db.execute(delete(ArenaQueue).where(ArenaQueue.player_id == player_id))
        self.db.commit()

    def get_queue(self):
        return self.db.execute(
            select(ArenaQueue).order_by(ArenaQueue.joined_at)
        ).scalars().all()

    def find_match(self):
        queue = self.get_queue()
        print(f"[DEBUG] Matching... Queue size: {len(queue)}")
        matched_pairs = []
        used_ids = set()

        for i in range(len(queue)):
            p1 = queue[i].player_id
            if p1 in used_ids:
                continue

            power1 = self.ship_service.get_ship_stats(p1)["power_score"]

            for j in range(i + 1, len(queue)):
                p2 = queue[j].player_id
                if p2 in used_ids:
                    continue

                power2 = self.ship_service.get_ship_stats(p2)["power_score"]

                weak, strong = sorted([power1, power2])

                #if strong <= weak * 1.2:
                #    matched_pairs.append((p1, p2))
                #    used_ids.update([p1, p2])
                #    break
                if strong <= weak * 12:
                    matched_pairs.append((p1, p2))
                    used_ids.update([p1, p2])
                    break
        print(f"[DEBUG] Matching... Queue size: {len(queue)}")
        return matched_pairs

    def resolve_battle(self, player1_id: int, player2_id: int) -> dict:
        stats1 = self.ship_service.get_ship_stats(player1_id)
        stats2 = self.ship_service.get_ship_stats(player2_id)

        score1 = stats1["power_score"]
        score2 = stats2["power_score"]

        if abs(score1 - score2) < 0.01:
            result = "draw"
            winner = None
            loser = None
        elif score1 > score2:
            result = "win1"
            winner, loser = player1_id, player2_id
        else:
            result = "win2"
            winner, loser = player2_id, player1_id

        new_health = None
        if loser:
            loser_ship = self.db.execute(
                select(Ship).where(Ship.player_id == loser)
            ).scalar_one()
            max_health = self.ship_service.get_hull_stats(loser)["max_health_hull"]
            new_health = max(0.0, float(loser_ship.health) - 0.1 * float(max_health))
            
            loser_ship.health = new_health

        # Записываем бой в таблицу
        self.db.add(ArenaFight(
            player1_id=player1_id,
            player2_id=player2_id,
            result=result
        ))

        # Удаление из очереди
        self.leave_queue(player1_id)
        self.leave_queue(player2_id)

        self.db.commit()

        return {
            "result": result,
            "winner": winner,
            "loser": loser,
            "loser_health_after": new_health,
        }

    async def notify_players_about_fight(self, player1_id: int, player2_id: int, result_data: dict, bot: Bot):
        try:
            text1 = self._build_fight_result_text(player1_id, player2_id, result_data)
            text2 = self._build_fight_result_text(player2_id, player1_id, result_data)

            await bot.send_message(chat_id=player1_id, text=text1, parse_mode=ParseMode.HTML)
            await bot.send_message(chat_id=player2_id, text=text2, parse_mode=ParseMode.HTML)

            print(f"[NOTIFY] Уведомления отправлены {player1_id} и {player2_id}")

        except Exception as e:
            print(f"[ERROR] Не удалось отправить уведомления: {str(e)}")

    def _build_fight_result_text(self, player_id: int, opponent_id: int, result_data: dict) -> str:
        winner = result_data.get("winner")
        loser = result_data.get("loser")
        draw = result_data.get("result") == "draw"
        lost_hp = result_data.get("loser_health_after")

        if draw:
            return f"<b>Результат боя:</b> Ничья!\nВы сразились с игроком <code>{opponent_id}</code> и бой завершился ничьей."

        if player_id == winner:
            return f"""<b>Результат боя:</b> Победа! 

Вы победили игрока <code>{opponent_id}</code>!

Урон по противнику: <b>{lost_hp:.0f}</b> HP"""
        else:
            return f"""<b>Результат боя:</b> Поражение... 

Вы проиграли игроку <code>{opponent_id}</code>!

Ваше здоровье после боя: <b>{lost_hp:.0f}</b> HP"""