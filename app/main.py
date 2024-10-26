from fastapi import FastAPI
import importlib
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel

app = FastAPI(
    title="Conqueria Caps Backend",
    docs_url="/",                 # Swagger UI at root
    openapi_url="/openapi.json",   # OpenAPI schema JSON at this URL
    redoc_url="/redoc"             # ReDoc URL
)

# Define a simple Bearer token scheme
http_bearer = HTTPBearer()

# Call the function to load all routes
def load_routes(app: FastAPI):
    """Dynamically load and include routes from all apps."""
    apps_dir = os.path.join(os.path.dirname(__file__), ".")
    for app_name in os.listdir(apps_dir):
        app_path = os.path.join(apps_dir, app_name)
        if os.path.isdir(app_path) and os.path.exists(os.path.join(app_path, "routes.py")):
            module_name = f"app.{app_name}.routes"
            module = importlib.import_module(module_name)
            app.include_router(module.router)

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

# Backup the original openapi method
original_openapi = app.openapi

# OpenAPI schema modifications to allow Bearer token input
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = original_openapi()

    # Add security scheme for Bearer token (NOT OAuth2)
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # Set global security for the endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if "security" not in openapi_schema["paths"][path][method]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/")
def read_root():
    return {"message": "Welcome to the Strategy Board Game!"}

# Load routes
load_routes(app)
