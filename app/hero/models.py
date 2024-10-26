from sqlalchemy import Column, String, Integer
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class Hero(Base):
    __tablename__ = "heroes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rarity = Column(String, nullable=False)  # e.g., Common, Rare, Legendary
    civ = Column(String, nullable=False)  # Civilization
    role = Column(String, nullable=False)
    picture = Column(String, nullable=True)  # Path to image
    description = Column(String, nullable=True)
    catch_phrase = Column(String, nullable=True)
    bonus_description = Column(String, nullable=True)
    shop_cost = Column(Integer, nullable=False)

    # Relationships
    # Users who have this hero set as primary
    users = relationship("User", back_populates="hero")
