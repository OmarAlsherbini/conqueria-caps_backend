from fastapi import FastAPI
import importlib
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Conqueria Caps Backend",
    docs_url="/",                 # Swagger UI at root
    openapi_url="/openapi.json",   # OpenAPI schema JSON at this URL
    redoc_url="/redoc"                # ReDoc URL
)

def load_routers(app: FastAPI):
    """Dynamically load and include routers from all apps."""
    apps_dir = os.path.join(os.path.dirname(__file__), "..", "apps")
    for app_name in os.listdir(apps_dir):
        app_path = os.path.join(apps_dir, app_name)
        if os.path.isdir(app_path):
            try:
                # Import the routers.py module dynamically
                module = importlib.import_module(f"apps.{app_name}.routers")
                if hasattr(module, "router"):
                    app.include_router(module.router)
                    print(f"Loaded router from {app_name}")
            except ModuleNotFoundError:
                print(f"No router found in {app_name}")
                continue


@app.get("/")
def read_root():
    return {"message": "Welcome to the Strategy Board Game!"}

# Call the function to load all routers
load_routers(app)

# CORS setup
origins = [
    "http://localhost",
    "http://localhost:3000",  # Adjust this based on frontend domain/port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

