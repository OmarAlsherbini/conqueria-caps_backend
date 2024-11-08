import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.attack_unit.models import AttackUnit
import os

# Path to the JSON file
attack_units_json_path = os.path.join(os.path.dirname(__file__), 'data', 'attack_units.json')

async def load_attack_units(db: AsyncSession):
    # Check if attack units are already loaded
    result = await db.execute("SELECT * FROM attack_units LIMIT 1")
    existing_unit = result.fetchone()

    if existing_unit:
        print("Attack units are already loaded.")
        return

    # Load attack units from the JSON file
    with open(attack_units_json_path, 'r') as file:
        units = json.load(file)
    
    # Insert attack units into the database
    for unit_data in units:
        new_unit = AttackUnit(**unit_data)
        db.add(new_unit)

    await db.commit()
    print("Attack units loaded successfully.")
