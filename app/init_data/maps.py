import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.map.models import Map
import os

# Path to the JSON file
maps_json_path = os.path.join(os.path.dirname(__file__), 'data', 'maps.json')

async def load_maps(db: AsyncSession):
    # Check if there are any maps in the database already
    result = await db.execute("SELECT * FROM maps LIMIT 1")
    existing_map = result.fetchone()

    if existing_map:
        print("Maps are already loaded.")
        return
    
    # Load maps from the JSON file
    with open(maps_json_path, 'r') as file:
        maps = json.load(file)
    
    # Insert maps into the database
    for map_data in maps:
        new_map = Map(**map_data)
        db.add(new_map)
    
    await db.commit()
    print("Maps loaded successfully.")
