from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import user
from routes import gpt
from models import user as user_models
from config.database import engine

origins = [
    "*"
]
def create_application():
    application = FastAPI()
    application.include_router(user.user_router)
    application.include_router(user.guest_router)
    application.include_router(user.auth_router)
    application.include_router(gpt.gpt_router)
    
    return application


app = create_application()

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

user_models.Base.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Running!"}