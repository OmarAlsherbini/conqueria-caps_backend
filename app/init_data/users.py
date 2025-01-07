import json
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.authentication.models import User

# Load environment-specific .env file
env = os.getenv('ENVIRONMENT')
dotenv_path = f'.env.{env}'
load_dotenv(dotenv_path)

# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Path to the JSON file containing user data
users_json_path = os.path.join(os.path.dirname(__file__), 'data', 'users.json')

async def load_users(db: AsyncSession):
    # Check if users are already loaded
    result = await db.execute("SELECT * FROM users LIMIT 1")
    existing_user = result.fetchone()

    if existing_user:
        print("Users are already loaded.")
        return

    # Retrieve admin and user passwords from environment variables
    admin_password = os.getenv("ADMIN_PASSWORD")
    user_password = os.getenv("USER_PASSWORD")

    if not admin_password or not user_password:
        raise ValueError("Environment variables ADMIN_PASSWORD and USER_PASSWORD must be set.")

    # Load users from the JSON file
    with open(users_json_path, 'r') as file:
        users = json.load(file)

    # Insert users into the database with hashed passwords
    for user_data in users:
        # Use the appropriate password for each user
        if user_data["is_admin"]:
            user_data["hashed_password"] = pwd_context.hash(admin_password)
        else:
            user_data["hashed_password"] = pwd_context.hash(user_password)
        
        new_user = User(**user_data)
        db.add(new_user)

    await db.commit()
    print("Default users loaded successfully.")
