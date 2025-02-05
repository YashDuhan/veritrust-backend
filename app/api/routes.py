from fastapi import APIRouter
from .endpoints import root, health_check,check_image

app_router = APIRouter()

# Default route
app_router.get("/")(root)

# Health check route
app_router.get("/health")(health_check)

# Check Image's Content
app_router.post("/check-image")(check_image)

