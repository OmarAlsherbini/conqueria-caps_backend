import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.building.models import DefensiveBuilding
import os

# Path to the JSON file
defensive_buildings_json_path = os.path.join(os.path.dirname(__file__), 'data', 'defensive_buildings.json')

async def load_defensive_buildings(db: AsyncSession):
    # Check if defensive buildings are already loaded
    result = await db.execute("SELECT * FROM defensive_buildings LIMIT 1")
    existing_building = result.fetchone()

    if existing_building:
        print("Defensive buildings are already loaded.")
        return

    # Load defensive buildings from the JSON file
    with open(defensive_buildings_json_path, 'r') as file:
        buildings = json.load(file)
    
    # Insert defensive buildings into the database
    for building_data in buildings:
        new_building = DefensiveBuilding(**building_data)
        db.add(new_building)

    await db.commit()
    print("Defensive buildings loaded successfully.")
