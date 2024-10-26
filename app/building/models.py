from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
from app.db.base_class import Base
from sqlalchemy.ext.declarative import declared_attr

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Generative or Defensive
    picture = Column(String, nullable=True)  # Path to image
    health_points = Column(Float, nullable=False)
    cost = Column(Integer, nullable=False)
    turns_to_build = Column(Integer, nullable=False)
    experience = Column(Integer, nullable=False)
    upgrade_threshold = Column(Integer, nullable=False)
    shop_cost = Column(Integer, nullable=False)
    rarity = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tech_tree = Column(String, nullable=True)  # Placeholder for future tech tree implementation

    # Polymorphic setup: `Building` is abstract
    type = Column(String, nullable=False)
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
    can_attack_air = Column(Boolean, default=False)
    accuracy = Column(Float, nullable=False)
    attack_sound = Column(String, nullable=True)
    mode = Column(String, nullable=False)  # Single-target or Multi-target
    damage_radius = Column(Float, nullable=True)  # Applicable for multi-target mode
    level = Column(Integer, default=1)

    __mapper_args__ = {
        'polymorphic_identity': 'defensive',
    }


class GenerativeBuilding(Building):
    __tablename__ = "generative_buildings"

    id = Column(Integer, ForeignKey('buildings.id'), primary_key=True)
    money = Column(Integer, nullable=False)
    turns = Column(Integer, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'generative',
    }
