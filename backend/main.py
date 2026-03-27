from fastapi import FastAPI
from routers import auth_routes, detection_routes
import models
from database import engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="TruthShield AI")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_routes.router)
app.include_router(detection_routes.router)

@app.get("/")
def home():
    return {"message": "TruthShield AI running"}