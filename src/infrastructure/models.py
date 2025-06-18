from datetime import datetime

from sqlalchemy import Column, Integer, String, \
    ForeignKey, DateTime, Boolean, BigInteger, Numeric, Sequence, func, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, relationship
from src.application.config_loader import config

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    players_guns = relationship("PlayerGun", back_populates="player", cascade="all, delete-orphan")
    players_hulls = relationship("PlayerHull", back_populates="player", cascade="all, delete-orphan")
    ships = relationship("Ship", back_populates="player", cascade="all, delete-orphan")
    arena_status = relationship("ArenaQueue", back_populates="player", uselist=False, cascade="all, delete-orphan")
    resources = relationship("PlayerResources", back_populates="player", uselist=False, cascade="all, delete-orphan")


class PlayerResources(Base):
    __tablename__ = 'player_resources'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    player_id = Column(BigInteger, ForeignKey('players.id', ondelete='CASCADE'), unique=True, nullable=False)
    metals = Column(Integer, default=config["game"]['initial_resources'], nullable=False)
    crystalls = Column(Integer, default=config["game"]['initial_resources'], nullable=False)
    gas = Column(Integer, default=config["game"]['initial_resources'], nullable=False)

    player = relationship("Player", back_populates="resources")


class GunTemplate(Base):
    __tablename__ = 'gun_templates'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), nullable=False)

    base_damage = Column(Numeric, nullable=False)
    base_crit_rate = Column(Numeric, nullable=False)
    base_crit_damage = Column(Numeric, nullable=False)
    base_speed = Column(Numeric, nullable=False)

    gain_damage = Column(Numeric, nullable=True)
    gain_crit_rate = Column(Numeric, nullable=True)
    gain_crit_damage = Column(Numeric, nullable=True)
    gain_speed = Column(Numeric, nullable=True)

    players_guns = relationship("PlayerGun", back_populates="template", cascade="all, delete-orphan")


class PlayerGun(Base):
    __tablename__ = 'players_guns'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    player_id = Column(BigInteger, ForeignKey('players.id', ondelete='CASCADE'), nullable=False)
    gun_id = Column(Integer, ForeignKey('gun_templates.id'), nullable=False)
    current_level = Column(Integer, default=0)
    is_equipped = Column(Boolean, default=False)

    player = relationship("Player", back_populates="players_guns")
    template = relationship("GunTemplate", back_populates="players_guns")


class HullTemplate(Base):
    __tablename__ = 'hull_templates'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), nullable=False)

    base_armor = Column(Numeric, nullable=False)
    base_max_shields = Column(Numeric, nullable=False)
    base_max_health = Column(Numeric, nullable=False)
    base_maneuver = Column(Numeric, nullable=False)

    gain_armor = Column(Numeric, nullable=True)
    gain_max_shields = Column(Numeric, nullable=True)
    gain_max_health = Column(Numeric, nullable=True)
    gain_maneuver = Column(Numeric, nullable=True)

    players_hulls = relationship("PlayerHull", back_populates="hull_template", cascade="all, delete-orphan")


class PlayerHull(Base):
    __tablename__ = 'players_hulls'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    player_id = Column(BigInteger, ForeignKey('players.id', ondelete='CASCADE'), nullable=False)
    hull_id = Column(Integer, ForeignKey('hull_templates.id'), nullable=False)
    current_level = Column(Integer, default=0)
    is_equipped = Column(Boolean, default=False)

    player = relationship("Player", back_populates="players_hulls")
    hull_template = relationship("HullTemplate", back_populates="players_hulls")


class Ship(Base):
    __tablename__ = 'ships'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    player_id = Column(BigInteger, ForeignKey('players.id', ondelete='CASCADE'), nullable=False)
    player_hull_id = Column(Integer, ForeignKey('players_hulls.id', ondelete='CASCADE'), nullable=False)
    player_gun_id = Column(Integer, ForeignKey('players_guns.id', ondelete='CASCADE'), nullable=False)
    health = Column(Numeric, nullable=False)
    shields = Column(Numeric, nullable=False)
    repair_ends_at = Column(DateTime, nullable=True)

    player = relationship("Player", back_populates="ships")
    player_hull = relationship("PlayerHull")
    player_gun = relationship("PlayerGun")


class ArenaQueue(Base):
    __tablename__ = "arena_queue"

    player_id = Column(BigInteger, ForeignKey("players.id", ondelete='CASCADE'), primary_key=True)
    joined_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    player = relationship("Player", back_populates="arena_status")


class ArenaFight(Base):
    __tablename__ = 'arena_fights'

    id = Column(Integer, primary_key=True, autoincrement=True)
    player1_id = Column(BigInteger, nullable=False)
    player2_id = Column(BigInteger, nullable=False)
    result = Column(String(10), nullable=False)


class UTMtag(Base):
    __tablename__ = 'utm_tags'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tag = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used = Column(Integer, default=0, nullable=True)


class ScreenView(Base):
    __tablename__ = 'screen_views'
    __table_args__ = (
        PrimaryKeyConstraint('player_id', 'screen_key'),
    )

    player_id = Column(BigInteger, ForeignKey('players.id', ondelete='CASCADE'), nullable=False)
    screen_key = Column(String, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)

    player = relationship("Player", backref="screen_views")

