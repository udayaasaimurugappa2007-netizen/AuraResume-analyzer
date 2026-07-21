import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from app.routes.analyze import router as analyze_router
from app.models.database import init_db
from app.config import UPLOAD_DIR, BASE_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("resume_analyzer.main")

app = FastAPI(
    title="Premium AI Resume Analyzer API",
    description="Scalable backend API for analyzing, scoring, and matching resumes using Google Gemini AI.",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend dist directory path
FRONTEND_DIST_DIR = os.path.normpath(
    os.path.join(BASE_DIR, "..", "frontend", "dist")
)

# Startup event
@app.on_event("startup")
async def startup_db_client():
    logger.info("Initializing database connection...")
    await init_db()
    logger.info(f"Frontend dist directory: {FRONTEND_DIST_DIR}")
    logger.info(f"Frontend dist exists: {os.path.exists(FRONTEND_DIST_DIR)}")

# Mount uploaded resumes static folder
if os.path.exists(UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include API routes (all under /api prefix)
app.include_router(analyze_router)

# SPA + static assets catch-all handler
# This serves:
#   - /assets/... → actual files from dist/assets/
#   - /favicon.ico, /logo.svg etc → actual files from dist/
#   - /upload, /dashboard/... → index.html (React Router SPA)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Try to find an actual file in the dist directory first
    if full_path:
        candidate = os.path.normpath(os.path.join(FRONTEND_DIST_DIR, full_path))
        # Security: ensure the path stays inside dist
        if candidate.startswith(FRONTEND_DIST_DIR) and os.path.isfile(candidate):
            # Explicitly determine media type by extension to avoid Windows registry corruption
            ext = os.path.splitext(candidate)[1].lower()
            media_type = None
            if ext == ".css":
                media_type = "text/css"
            elif ext == ".js":
                media_type = "application/javascript"
            elif ext == ".svg":
                media_type = "image/svg+xml"
            elif ext == ".png":
                media_type = "image/png"
            elif ext == ".jpg" or ext == ".jpeg":
                media_type = "image/jpeg"
            elif ext == ".ico":
                media_type = "image/x-icon"
            elif ext == ".json":
                media_type = "application/json"
            elif ext == ".html":
                media_type = "text/html"
            
            return FileResponse(candidate, media_type=media_type)

    # Fall back to index.html for all SPA routes
    index_html = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if os.path.isfile(index_html):
        return FileResponse(index_html, media_type="text/html")

    return JSONResponse(status_code=404, content={"detail": "Not found"})

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

