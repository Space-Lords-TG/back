from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from sqlalchemy import BigInteger, Numeric

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    ships = relationship("Ship", back_populates="player", cascade="all, delete-orphan")


class Gun(Base):
    __tablename__ = 'guns'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    damage = Column(Integer, nullable=False)
    crit_rate = Column(Numeric(7, 5), nullable=False)
    crit_damage = Column(Numeric(7, 2), nullable=False)
    speed = Column(Numeric(7, 2), nullable=False)
    power_score = Column(Numeric(7, 2), nullable=False)

    ships = relationship("Ship", back_populates="gun")

class Hull(Base):
    __tablename__ = 'hulls'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    armor = Column(Integer, nullable=False)
    max_shields = Column(Integer, nullable=False)
    max_health = Column(Integer, nullable=False)
    maneuver = Column(Integer, nullable=False)
    power_score = Column(Integer, nullable=False)

    ships = relationship("Ship", back_populates="hull")


class Ship(Base):
    __tablename__ = 'ships'

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(BigInteger, ForeignKey('players.id'), nullable=False)
    hull_id = Column(Integer, ForeignKey('hulls.id'), nullable=False)
    gun_id = Column(Integer, ForeignKey('guns.id'), nullable=False)
    health = Column(Integer, nullable=False)
    shields = Column(Integer, nullable=False)
    power_score = Column(Integer, nullable=False)

    player = relationship("Player", back_populates="ships")
    hull = relationship("Hull", back_populates="ships")
    gun = relationship("Gun", back_populates="ships")
