from sqlalchemy import Column, String, Integer, Boolean, Float
from app.db.base_class import Base

class AttackUnit(Base):
    __tablename__ = "attack_units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    picture = Column(String, nullable=True)  # Path to image
    cost = Column(Integer, nullable=False)
    health_points = Column(Float, nullable=False)
    damage = Column(Float, nullable=False)
    speed = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    max_number_per_line = Column(Integer, nullable=False)
    is_air = Column(Boolean, default=False)
    is_sea = Column(Boolean, default=False)
    turns_to_build = Column(Integer, nullable=False)
    experience_value = Column(Integer, nullable=False)
    shop_cost = Column(Integer, nullable=False)
    rarity = Column(String, nullable=False)
    description = Column(String, nullable=True)
