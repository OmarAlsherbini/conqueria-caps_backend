from sqlalchemy import Column, String, Integer
from app.db.base_class import Base
from sqlalchemy.orm import relationship
from app.authentication.models import User

class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code_2 = Column(String(2), nullable=False)  # 2-letter code
    code_3 = Column(String(3), nullable=False)  # 3-letter code
    flag = Column(String, nullable=True)  # Path or URL to the flag image

    # Relationships
    users = relationship("User", back_populates="country")
