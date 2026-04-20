from fastapi import FastAPI
from microservices.auth.app.routes import router as auth_router

# init FastAPI
app = FastAPI(
    title="Amass Delta Auth Service",
    version="1.0.0"
)

app.include_router(auth_router)