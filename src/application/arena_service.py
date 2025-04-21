from sqlalchemy.orm import Session
from sqlalchemy import select, delete
# from datetime import datetime, timezone
from src.infrastructure.models import ArenaQueue, Ship, ArenaFight
from src.application.ship_service import ShipService
from src.application.player_service import PlayerService
from telegram import Bot
from telegram.constants import ParseMode
# import asyncio
# from io import BytesIO
import random
from decimal import Decimal

class ArenaService:
    def __init__(self, db: Session):
        self.db = db
        self.ship_service = ShipService(db)
        self.player_service = PlayerService(db)

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
    
    def simulate_battle(self, stats1, stats2, username1, username2):
        log = []
        
        # Копируем здоровье и щиты для изменения
        ship1 = stats1.copy()
        ship2 = stats2.copy()
        ship1['shields'] = stats1['shields_hull']
        ship2['shields'] = stats2['shields_hull']
        ship1['health'] = Decimal(ship1['health'])
        ship2['health'] = Decimal(ship2['health'])

        def attack(attacker, defender, attacker_name, defender_name):
            # Учитываем шанс промаха, зависящий от маневренности
            if random.random() < defender['maneuver_hull']:
                log.append(f"{attacker_name} атакует {defender_name}, но промахивается!")
                return

            base_damage = attacker['damage_gun']
            # Коэффицент урона варьируется от 0.8 до 1.2
            multiplier = 1 + 0.2 * (1 - random.random() * 2)
            base_damage *= multiplier

            crit = random.random() < (attacker['crit_rate_gun'] / 100)
            if crit:
                base_damage *= attacker['crit_damage_gun']
                log.append(f"{attacker_name} наносит критический урон!")

            # Снижение урона за счёт брони
            final_damage = max(0, base_damage - defender['armor_hull'])

            # Сначала урон по щитам
            if defender['shields'] > 0:
                absorbed = min(defender['shields'], final_damage)
                defender['shields'] -= absorbed
                final_damage -= absorbed
                log.append(f"{attacker_name} пробивает щиты {defender_name}\
                            на {absorbed:.1f} урона. Прочность щитов: \
                                {defender['shields']:.1f}")

            # Затем оставшийся урон по здоровью
            if final_damage > 0:
                defender['health'] -= Decimal(final_damage)
                if defender['health'] < 0: 
                    defender['health'] = 0
                log.append(f"{attacker_name} наносит {defender_name} \
                           {final_damage:.1f} урона по корпусу. Осталось HP: \
                            {defender['health']:.1f}")

        # Определяем, кто ходит первым по скорости
        turn = 0  # 0 - игрок 1, 1 - игрок 2
        if stats2['speed_gun'] > stats1['speed_gun']:
            turn = 1

        while ship1['health'] > 0 and ship2['health'] > 0:
            if turn == 0:
                attack(ship1, ship2, username1, username2)
                if ship2['health'] <= 0:
                    log.append(f"{username2} нокаутирован!")
                    return "win1", "\n".join(log)
            else:
                attack(ship2, ship1, username1, username2)
                if ship1['health'] <= 0:
                    log.append(f"{username1} нокаутирован!")
                    return "win2", "\n".join(log)
            turn = 1 - turn  # Меняем ход

    def resolve_battle(self, player1_id: int, player2_id: int) -> dict:
        stats1 = self.ship_service.get_ship_stats(player1_id)
        stats2 = self.ship_service.get_ship_stats(player2_id)

        username1 = self.player_service.get_username(player1_id)
        username2 = self.player_service.get_username(player2_id)

        # score1 = stats1["power_score"]
        # score2 = stats2["power_score"]

        result, battleLog = self.simulate_battle(stats1, stats2, username1, username2)

        if result == "win1":
            winner, loser = player1_id, player2_id
        else:
            winner, loser = player2_id, player1_id

        # if abs(score1 - score2) < 0.01:
        #     result = "draw"
        #     winner = None
        #     loser = None
        # elif score1 > score2:
        #     result = "win1"
        #     winner, loser = player1_id, player2_id
        # else:
        #     result = "win2"
        #     winner, loser = player2_id, player1_id

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
            "battle_log": battleLog
        }

    async def notify_players_about_fight(self, player1_id: int, player2_id: int, result_data: dict, bot: Bot):
        try:
            text1 = self._build_fight_result_text(player1_id, player2_id, result_data)
            text2 = self._build_fight_result_text(player2_id, player1_id, result_data)

            # battleLog = result_data.get("battle_log")

            # log_text = "\n".join(battleLog)
            # file = BytesIO(log_text.encode("utf-8"))
            # fileID = str(random.random())
            # file.name = f"battle_log_{fileID}.txt"

            await bot.send_message(chat_id=player1_id, text=text1, parse_mode=ParseMode.HTML)
            await bot.send_message(chat_id=player2_id, text=text2, parse_mode=ParseMode.HTML)

            print(f"[NOTIFY] Уведомления отправлены {player1_id} и {player2_id}")

        except Exception as e:
            print(f"[ERROR] Не удалось отправить уведомления: {str(e)}")

    def _build_fight_result_text(self, player_id: int, opponent_id: int, result_data: dict) -> str:
        winner = result_data.get("winner")
        # loser = result_data.get("loser")
        # draw = result_data.get("result") == "draw"
        lost_hp = result_data.get("loser_health_after")
        battleLog = result_data.get("battle_log")

        # if draw:
        #     return f"<b>Результат боя:</b> Ничья!\nВы \
        # сразились с игроком <code>{opponent_id}</code> и бой завершился ничьей."

        if player_id == winner:
            return f"""<b>Результат боя:</b> Победа!
Урон по противнику: <b>{lost_hp:.0f}</b> HP.
Лог боя:
<pre>
{battleLog}
</pre>"""
        else:
            return f"""<b>Результат боя:</b> Поражение.
Ваше здоровье после боя: <b>{lost_hp:.0f}</b> HP.
Лог боя:
<pre>
{battleLog}
</pre>"""