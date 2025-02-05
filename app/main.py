import os
import sys
from fastapi import FastAPI
# Module for CORS
from fastapi.middleware.cors import CORSMiddleware
# Routes are declared in this Directory
from app.api.routes import app_router
from dotenv import load_dotenv

# Check if running in dev container or Vercel only
if not (os.getenv('IS_DEVCONTAINER') or os.getenv('VERCEL')):
    print("\nThis application can only run inside a dev container or on Vercel\n")
    # Forcefully exit the app
    sys.exit(1)

app = FastAPI(title="VeriTrust Backend")

# To enable cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include the router
app.include_router(app_router)

load_dotenv()  # This loads the environment variables from .env