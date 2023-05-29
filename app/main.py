from fastapi import FastAPI
from .database import engine
from .models import Base
from .routers import question

Base.metadata.create_all(bind=engine)

# Создаем экземпляр приложения FastAPI
app = FastAPI(
    title='Trivia-Quiz-API'
)

app.include_router(question.router)


@app.get('/')
async def root():
    return {"message": "Hello guys! Thanks for your time!"}