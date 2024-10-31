from pydantic import BaseModel
from typing import List, Optional

class BuildingSlotBase(BaseModel):
    territory_id: int
    owner_id: int
    location: List[float]

class BuildingSlotCreate(BuildingSlotBase):
    pass

class BuildingSlotUpdate(BaseModel):
    deployed_defensive_building_id: Optional[int] = None
    deployed_generative_building_id: Optional[int] = None

class BuildingSlotDetail(BuildingSlotBase):
    id: int
    deployed_defensive_building_id: Optional[int]
    deployed_generative_building_id: Optional[int]

    class Config:
        from_attributes  = True
