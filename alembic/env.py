import os
import importlib
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Load .env file
env = os.getenv('ENVIRONMENT')
dotenv_path = f'.env.{env}'
load_dotenv(dotenv_path)

# Get the alembic config object
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Build the connection URL from environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST")
POSTGRES_PORT = 5432

database_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
config.set_main_option("sqlalchemy.url", database_url)

# Set environment-specific migrations folder
if env == 'dev':
    version_path = 'alembic/migrations/dev_versions'
elif env == 'prod':
    version_path = 'alembic/migrations/prod_versions'
elif env == 'test':
    version_path = 'alembic/migrations/test_versions'
else:
    raise ValueError("Unknown environment")

# Dynamically import models from each service
def get_models_metadata():
    services_dir = os.path.join(os.path.dirname(__file__), "../app")
    metadata_list = []
    for service_name in os.listdir(services_dir):
        service_path = os.path.join(services_dir, service_name)
        if os.path.isdir(service_path):
            try:
                models_module = importlib.import_module(f"app.{service_name}.models")
                if hasattr(models_module, "Base"):
                    metadata_list.append(models_module.Base.metadata)
                    print(f"Loaded metadata from {service_name}")
            except ModuleNotFoundError:
                print(f"No models found in {service_name}")
                continue
    return metadata_list

# Combine metadata from all services
target_metadata = get_models_metadata()

# Define the migration logic for offline and online modes
def run_migrations_offline():
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        config.set_main_option("script_location", version_path)
        config.set_main_option("version_locations", version_path)
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            config.set_main_option("script_location", version_path)
            config.set_main_option("version_locations", version_path)
            context.run_migrations()



config.set_main_option("script_location", version_path)
config.set_main_option("version_locations", version_path)

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
