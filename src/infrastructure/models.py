from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, BigInteger, Numeric
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    players_guns = relationship("PlayerGun", back_populates="player")
    players_hulls = relationship("PlayerHull", back_populates="player")
    ships = relationship("Ship", back_populates="player")

class GunTemplate(Base):
    __tablename__ = 'gun_templates'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), nullable=False)

    base_damage = Column(Numeric(7, 2), nullable=False)
    base_crit_rate = Column(Numeric(7, 2), nullable=False)
    base_crit_damage = Column(Numeric(7, 2), nullable=False)
    base_speed = Column(Numeric(7, 2), nullable=False)

    gain_damage = Column(Numeric(7, 2), nullable=True)
    gain_crit_rate = Column(Numeric(7, 2), nullable=True)
    gain_crit_damage = Column(Numeric(7, 2), nullable=True)
    gain_speed = Column(Numeric(7, 2), nullable=True)

    players_guns = relationship("PlayerGun", back_populates="template")

class PlayerGun(Base):
    __tablename__ = 'players_guns'

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(BigInteger, ForeignKey('players.id'), nullable=False)
    gun_id = Column(Integer, ForeignKey('gun_templates.id'), nullable=False)
    current_level = Column(Integer, default=1)
    is_equipped = Column(Boolean, default=False)
    template = relationship("GunTemplate", back_populates="players_guns")

    player = relationship("Player", back_populates="players_guns")


class HullTemplate(Base):
    __tablename__ = 'hull_templates'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), nullable=False)

    base_armor = Column(Numeric(7, 2), nullable=False)
    base_max_shields = Column(Numeric(7, 2), nullable=False)
    base_max_health = Column(Numeric(7, 2), nullable=False)
    base_maneuver = Column(Numeric(7, 2), nullable=False)

    gain_armor = Column(Numeric(7, 2), nullable=True)
    gain_max_shields = Column(Numeric(7, 2), nullable=True)
    gain_max_health = Column(Numeric(7, 2), nullable=True)
    gain_maneuver = Column(Numeric(7, 2), nullable=True)

    players_hulls = relationship("PlayerHull", back_populates="hull_template")


class PlayerHull(Base):
    __tablename__ = 'players_hulls'

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(BigInteger, ForeignKey('players.id'), nullable=False)
    hull_id = Column(Integer, ForeignKey('hull_templates.id'), nullable=False)
    current_level = Column(Integer, default=1)
    is_equipped = Column(Boolean, default=False)

    player = relationship("Player", back_populates="players_hulls")
    hull_template = relationship("HullTemplate", back_populates="players_hulls")


class Ship(Base):
    __tablename__ = 'ships'

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(BigInteger, ForeignKey('players.id'), nullable=False)
    player_hull_id = Column(Integer, ForeignKey('players_hulls.id'), nullable=False)
    player_gun_id = Column(Integer, ForeignKey('players_guns.id'), nullable=False)
    health = Column(Numeric(7, 2), nullable=False)
    shields = Column(Numeric(7, 2), nullable=False)

    player = relationship("Player", back_populates="ships")
    player_hull = relationship("PlayerHull")
    player_gun = relationship("PlayerGun")
