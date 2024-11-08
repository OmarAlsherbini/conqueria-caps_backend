from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
from app.db.base_class import Base
from sqlalchemy.ext.declarative import declared_attr

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Generative or Defensive
    picture = Column(String, nullable=True)  # Path to image
    in_game_picture = Column(String, nullable=True)  # Path to image
    health_points = Column(Float, nullable=False)
    cost = Column(Integer, nullable=False)
    turns_to_build = Column(Integer, nullable=False)
    upgrade_threshold = Column(Integer, nullable=False)
    shop_cost = Column(Integer, nullable=False)
    rarity = Column(String, nullable=False)
    is_alien = Column(Boolean, default=False)
    deploy_sound = Column(String, nullable=True)
    description = Column(String, nullable=True)
    tech_tree = Column(String, nullable=True)  # Placeholder for future tech tree implementation

    # Polymorphic setup: `Building` is abstract
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'building',
        'with_polymorphic': '*'
    }

    @declared_attr
    def __abstract__(cls):
        return True
    

class DefensiveBuilding(Building):
    __tablename__ = "defensive_buildings"

    id = Column(Integer, ForeignKey('buildings.id'), primary_key=True)
    damage = Column(Float, nullable=False)
    range = Column(Float, nullable=False)
    fire_rate = Column(Float, nullable=False)
    damage_per_second = Column(Float, nullable=False)
    can_attack_ground = Column(Boolean, default=False)
    can_attack_air = Column(Boolean, default=False)
    accuracy = Column(Float, nullable=False)
    air_accuracy = Column(Float, nullable=False)
    mode = Column(String, nullable=False)  # Single-target or Multi-target
    cone_angle = Column(Float, nullable=True)
    aoe = Column(Float, nullable=True)  # Applicable for multi-target mode
    projectile_speed = Column(Integer, nullable=True)
    level = Column(Integer, default=1)
    attack_sound = Column(String, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'defensive',
    }

class GenerativeBuilding(Building):
    __tablename__ = "generative_buildings"

    id = Column(Integer, ForeignKey('buildings.id'), primary_key=True)
    money = Column(Integer, nullable=False)
    alien_money = Column(Integer, nullable=False)
    turns = Column(Integer, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'generative',
    }
