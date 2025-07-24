from sqlalchemy.orm import Session
from sqlalchemy import select
import datetime

from src.application.config_loader import config
from src.infrastructure.models import (
    Player, PlayerGun, PlayerHull, PlayerResources, Ship, HullTemplate, ScreenView,
    PlayerTutorialFlags
)



class PlayerService:
    def __init__(self, db: Session):
        self.db = db

    def player_init(self, id: int, username: str):
        player = self.db.execute(
            select(Player).
            where(Player.id == id)
        ).scalar_one_or_none()

        if not player:
            created_at = datetime.datetime.now()
            newPlayer = Player(
                id=id,
                username=username,
                created_at=created_at
            )
            newPlayerResources = PlayerResources(
                player_id=id
            )
            newPlayerGun = PlayerGun(
                player_id=id,
                gun_id=1,
                is_equipped=True
            )
            newPlayerHull = PlayerHull(
                player_id=id,
                hull_id=1,
                is_equipped=True
            )
            # Добавляем флаги обучения
            newPlayerTutorialFlags = PlayerTutorialFlags(
                player_id=id
            )

            self.db.add(newPlayer)
            self.db.add(newPlayerResources)
            self.db.add(newPlayerGun)
            self.db.add(newPlayerHull)
            self.db.add(newPlayerTutorialFlags)
            self.db.commit()

            newShip = Ship(
                player_id=id,
                player_gun_id=newPlayerGun.id,
                player_hull_id=newPlayerHull.id,
                health=0,
                shields=0
            )

            self.db.add(newShip)
            self.db.commit()

            # Добавляем все оставшиеся оружия (неэкипированные)
            guns_count = config["game"]["guns_count"]
            for i in range(2, guns_count):
                anotherPlayerGun = PlayerGun(
                    player_id=id,
                    gun_id=i,
                    is_equipped=False
                )
                self.db.add(anotherPlayerGun)

            # Добавляем все оставшиеся корпуса (неэкипированные)
            hulls_count = config["game"]["hulls_count"]
            for i in range(2, hulls_count):
                anotherPlayerHull = PlayerHull(
                    player_id=id,
                    hull_id=i,
                    is_equipped=False
                )
                self.db.add(anotherPlayerHull)
            self.db.commit()

            # Пересчитываем параметры корабля
            self.recalculate_stats(newShip)
            self.db.commit()

            return newPlayer
        else:
            return player

    def recalculate_stats(self, ship: Ship):
        player_hull = self.db.get(
            PlayerHull,
            ship.player_hull_id
        )
        hull_template = self.db.get(
            HullTemplate,
            player_hull.hull_id
        )
        ship.health = self.calc(
            hull_template.base_max_health,
            hull_template.gain_max_health,
            player_hull.current_level
        )
        ship.shields = self.calc(
            hull_template.base_max_shields,
            hull_template.gain_max_shields,
            player_hull.current_level
        )

    def calc(self, base, gain, level):
        base = float(base)
        gain = float(gain) if gain else 0
        return base + gain * (level - 1)
    
    def get_new_users_count(self, interval: datetime.datetime):
        current_time = datetime.datetime.now()
        print(type(interval), type(current_time))
        start_time = current_time - interval
        
        result = self.db.execute(
            select(Player)
            .where(Player.created_at >= start_time)
            .where(Player.created_at <= current_time)
        ).all()

        return len(result)

    def get_id(self, username):
        player = self.db.execute(
            select(Player)
            .where(Player.username == username)
        ).scalar_one_or_none()
        
        return player.id if player else None

    def get_all(self):
        players = self.db.execute(
            select(Player)
        ).scalars().all()
        
        return players
    

    def get_username(self, player_id: int):
        player = self.db.execute(
            select(Player).
            where(Player.id == player_id)
        ).scalar_one_or_none()

        if not player:
            return None
        
        return player.username
    

    def get_resources(self, player_id: int):
        return self.db.execute(
            select(PlayerResources).
            where(PlayerResources.player_id == player_id)
        ).scalar_one()
        
    def set_resources(self, player_id: int, metals: int | None = None, crystalls: int | None = None, gas: int | None = None) -> bool:
        try:
            # Получаем текущие ресурсы игрока
            resources = self.db.execute(
                select(PlayerResources)
                .where(PlayerResources.player_id == player_id)
            ).scalar_one()

            # Обновляем только указанные ресурсы
            if metals is not None:
                if metals < 0:
                    return False
                resources.metals = metals

            if crystalls is not None:
                if crystalls < 0:
                    return False
                resources.crystalls = crystalls

            if gas is not None:
                if gas < 0:
                    return False
                resources.gas = gas

            self.db.commit()
            return True

        except Exception:
            self.db.rollback()
            return False

    def increment_screen_view(self, player_id: int, screen_key: str) -> None:
        screen_view = self.db.execute(
            select(ScreenView)
            .where(ScreenView.player_id == player_id)
            .where(ScreenView.screen_key == screen_key)
        ).scalar_one_or_none()

        if screen_view:
            screen_view.view_count += 1
        else:
            new_screen_view = ScreenView(
                player_id=player_id,
                screen_key=screen_key,
                view_count=1
            )
            self.db.add(new_screen_view)
        self.db.commit()

    def get_screen_view_count(self, player_id: int, screen_key: str) -> int:
        screen_view = self.db.execute(
            select(ScreenView)
            .where(ScreenView.player_id == player_id)
            .where(ScreenView.screen_key == screen_key)
        ).scalar_one_or_none()

        return screen_view.view_count if screen_view else 0

    def get_tutorial_flags(self, player_id: int) -> PlayerTutorialFlags:
        """Получает флаги обучения игрока"""
        tutorial_flags = self.db.execute(
            select(PlayerTutorialFlags)
            .where(PlayerTutorialFlags.player_id == player_id)
        ).scalar_one_or_none()

        if not tutorial_flags:
            # Создаем новые флаги со значениями False
            tutorial_flags = PlayerTutorialFlags(
                player_id=player_id,
                arena_tutorial_shown=False,
                ship_tutorial_shown=False,
                planet_tutorial_shown=False,
                default_tutorial_shown=False
            )
            self.db.add(tutorial_flags)
            self.db.commit()

        return tutorial_flags

    def should_show_tutorial(self, player_id: int, screen_key: str) -> bool:
        """Проверяет, нужно ли показать обучающее сообщение для экрана"""
        tutorial_flags = self.get_tutorial_flags(player_id)

        screen_flag_mapping = {
            config["screens"]["ARENA"]: tutorial_flags.arena_tutorial_shown,
            config["screens"]["SHIP"]: tutorial_flags.ship_tutorial_shown,
            config["screens"]["PLANET"]: tutorial_flags.planet_tutorial_shown,
            config["screens"]["DEFAULT"]: tutorial_flags.default_tutorial_shown
        }

        return not screen_flag_mapping.get(screen_key, True)

    def mark_tutorial_shown(self, player_id: int, screen_key: str) -> None:
        """Отмечает, что обучающее сообщение для экрана было показано"""
        tutorial_flags = self.get_tutorial_flags(player_id)

        screen_flag_mapping = {
            config["screens"]["ARENA"]: "arena_tutorial_shown",
            config["screens"]["SHIP"]: "ship_tutorial_shown",
            config["screens"]["PLANET"]: "planet_tutorial_shown",
            config["screens"]["DEFAULT"]: "default_tutorial_shown"
        }

        flag_field = screen_flag_mapping.get(screen_key)
        if flag_field:
            setattr(tutorial_flags, flag_field, True)
            self.db.commit()

    def reset_all_tutorial_flags(self, player_id: int) -> None:
        """Сбрасывает все флаги обучения игрока"""
        tutorial_flags = self.get_tutorial_flags(player_id)
        tutorial_flags.arena_tutorial_shown = False
        tutorial_flags.ship_tutorial_shown = False
        tutorial_flags.planet_tutorial_shown = False
        tutorial_flags.default_tutorial_shown = False
        self.db.commit()