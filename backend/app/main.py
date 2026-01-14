from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.api.endpoints import auth

app = FastAPI(
    title="SkinTech AI Consultant",
    description="Intelligent Skincare Consultant API with RAG and Time-Awareness",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Welcome to SkinTech AI Consultant API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
