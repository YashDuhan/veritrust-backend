from fastapi import APIRouter, UploadFile, File
from .endpoints import root, health_check, check_image, check_url,manual_check, check_raw

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
