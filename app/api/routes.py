from fastapi import APIRouter, UploadFile, File
from .endpoints import root, health_check, check_image, check_url,manual_check, check_raw ,suggestions, check_health, get_from_s3, ask_question

app_router = APIRouter()

# Default route
app_router.get("/")(root)

# Health check route
app_router.get("/health")(health_check)

# Check Image's Content
app_router.post("/check-image")(check_image)

# Check URL
app_router.post("/extract-url")(check_url)

# Manual check route 
app_router.post("/manual-check")(manual_check)

# Check Raw
app_router.post("/check-raw")(check_raw)

# Suggestions route
app_router.post("/suggestions")(suggestions)

# Check User's health
app_router.post("/check-health")(check_health)

# Get Explore data from S3
app_router.get("/get-from-s3")(get_from_s3)

# Chat route
app_router.post("/chat")(ask_question)