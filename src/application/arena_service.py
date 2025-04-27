from sqlalchemy.orm import Session
from sqlalchemy import select, delete
# from datetime import datetime, timezone
from src.infrastructure.models import ArenaQueue, ArenaFight
from src.application.ship_service import ShipService
from src.application.player_service import PlayerService
from telegram import Bot
from telegram.constants import ParseMode
# import asyncio
# from io import BytesIO
import random
from decimal import Decimal
from src.application.config_loader import config

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
                power_threshold = config["game"]["match_power_threshold"]

                if strong <= weak * power_threshold:
                    matched_pairs.append((p1, p2))
                    used_ids.update([p1, p2])
                    break
        return matched_pairs or []
    
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
                log.append(f"{attacker_name} пробивает щиты {defender_name} \
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
                    return "win1", "\n".join(log), ship1['health'], 0
            else:
                attack(ship2, ship1, username2, username1)
                if ship1['health'] <= 0:
                    log.append(f"{username1} нокаутирован!")
                    return "win2", "\n".join(log), ship2['health'], 0
            turn = 1 - turn  # Меняем ход

    def resolve_battle(self, player1_id: int, player2_id: int) -> dict:
        stats1 = self.ship_service.get_ship_stats(player1_id)
        stats2 = self.ship_service.get_ship_stats(player2_id)

        username1 = self.player_service.get_username(player1_id)
        username2 = self.player_service.get_username(player2_id)

        # score1 = stats1["power_score"]
        # score2 = stats2["power_score"]

        result, battleLog, hp_winner, hp_loser = self.simulate_battle(stats1, stats2, username1, username2)

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

        # new_health = None
        # if loser:
        #     loser_ship = self.db.execute(
        #         select(Ship).where(Ship.player_id == loser)
        #     ).scalar_one()
        #     max_health = self.ship_service.get_hull_stats(loser)["max_health_hull"]
        #     new_health = 0

        #     loser_ship.health = new_health

        win_multiplier = float(config["arena_rewards"]["win_multiplier"])
        loss_multiplier = float(config["arena_rewards"]["loss_multiplier"])
        spread_exponent = float(config["arena_rewards"]["spread_exponent"])

        def calculate_reward(power_self, power_enemy, victory: bool) -> float:
            K = win_multiplier if victory else loss_multiplier
            L = spread_exponent
            if power_enemy == 0:
                return 0
            modifier = (1 + (power_enemy - power_self) / power_enemy)
            modifier = max(modifier, 0)
            return power_self * K * (modifier ** L)

        reward_winner = calculate_reward(
            self.ship_service.get_ship_stats(winner)["power_score"],
            self.ship_service.get_ship_stats(loser)["power_score"],
            victory=True
        )

        reward_loser = calculate_reward(
            self.ship_service.get_ship_stats(loser)["power_score"],
            self.ship_service.get_ship_stats(winner)["power_score"],
            victory=False
        )

        winner_metal = reward_winner / 2
        winner_cryst = reward_winner / 2
        loser_metal = reward_loser / 2
        loser_cryst = reward_loser / 2

        winner_resources = self.player_service.get_resources(winner)
        winner_resources.metals += int(winner_metal)
        winner_resources.crystalls += int(winner_cryst)

        loser_resources = self.player_service.get_resources(loser)
        loser_resources.metals += int(loser_metal)
        loser_resources.crystalls += int(loser_cryst)

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
            "winer_health_after": hp_winner,
            "loser_health_after": hp_loser,
            "battle_log": battleLog,
            "winner_reward_metal": int(winner_metal),
            "winner_reward_crystall": int(winner_cryst),
            "loser_reward_metal": int(loser_metal),
            "loser_reward_crystall": int(loser_cryst),
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
            for player_id, text in [(player1_id, text1), (player2_id, text2)]:
                try:
                    await bot.send_message(chat_id=player_id, text=text, parse_mode=ParseMode.HTML)
                    print(f"[NOTIFY] Уведомление отправлено игроку {player_id}")
                except Exception as send_error:
                    print(f"[ERROR] Не удалось отправить сообщение игроку {player_id}: {str(send_error)}")

        except Exception as e:
            print(f"[ERROR] Ошибка в notify_players_about_fight: {str(e)}")

    def _build_fight_result_text(self, player_id: int, opponent_id: int, result_data: dict) -> str:
        winner = result_data.get("winner")
        # loser = result_data.get("loser")
        # draw = result_data.get("result") == "draw"
        lost_hp_winer = result_data.get("winer_health_after")
        lost_hp_loser = result_data.get("loser_health_after")
        battleLog = result_data.get("battle_log")

        # if draw:
        #     return f"<b>Результат боя:</b> Ничья!\nВы \
        # сразились с игроком <code>{opponent_id}</code> и бой завершился ничьей."
        winner_metal = result_data.get("winner_reward_metal")
        winner_cryst = result_data.get("winner_reward_crystall")
        loser_metal = result_data.get("loser_reward_metal")
        loser_cryst = result_data.get("loser_reward_crystall")

        if player_id == winner:
            return f"""<b>Результат боя:</b> Победа!

    Вы победили игрока <code>{opponent_id}</code>!

    <b>Награда:</b>
    • Металлы: +{winner_metal}
    • Кристаллы: +{winner_cryst}

    <b>Ваше здоровье после боя:</b> {lost_hp_winer:.0f} HP.

    <b>Лог боя:</b>
    <pre>{battleLog}</pre>"""
        else:
            return f"""<b>Результат боя:</b> Поражение...

    Вы проиграли игроку <code>{opponent_id}</code>.

    <b>Награда:</b>
    • Металлы: +{loser_metal}
    • Кристаллы: +{loser_cryst}

    <b>Ваше здоровье после боя:</b> {lost_hp_loser:.0f} HP.

    <b>Лог боя:</b>
    <pre>{battleLog}</pre>"""