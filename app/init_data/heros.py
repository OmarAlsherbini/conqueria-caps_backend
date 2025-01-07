import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.hero.models import Hero
import os

# Path to the JSON file
heroes_json_path = os.path.join(os.path.dirname(__file__), 'data', 'heroes.json')

async def load_heroes(db: AsyncSession):
    # Check if there are any heroes in the database already
    result = await db.execute("SELECT * FROM heroes LIMIT 1")
    existing_hero = result.fetchone()

    if existing_hero:
        print("Heroes are already loaded.")
        return
    
    # Load heroes from the JSON file
    with open(heroes_json_path, 'r') as file:
        heroes = json.load(file)
    
    # Insert heroes into the database
    for hero_data in heroes:
        new_hero = Hero(**hero_data)
        db.add(new_hero)
    
    await db.commit()
    print("Heroes loaded successfully.")
