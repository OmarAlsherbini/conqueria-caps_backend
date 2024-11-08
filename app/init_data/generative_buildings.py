import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.building.models import GenerativeBuilding
import os

# Path to the JSON file
generative_buildings_json_path = os.path.join(os.path.dirname(__file__), 'data', 'generative_buildings.json')

async def load_generative_buildings(db: AsyncSession):
    # Check if generative buildings are already loaded
    result = await db.execute("SELECT * FROM generative_buildings LIMIT 1")
    existing_building = result.fetchone()

    if existing_building:
        print("Generative buildings are already loaded.")
        return

    # Load generative buildings from the JSON file
    with open(generative_buildings_json_path, 'r') as file:
        buildings = json.load(file)
    
    # Insert generative buildings into the database
    for building_data in buildings:
        new_building = GenerativeBuilding(**building_data)
        db.add(new_building)

    await db.commit()
    print("Generative buildings loaded successfully.")
