import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings


# Создаем подключение к базе данных
DATABASE_URL = (f"postgresql://{settings.database_username}:{settings.database_password}@"
                f"{settings.database_hostname}:{settings.database_port}/{settings.database_name}")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для наших моделей SQLAlchemy
Base = sqlalchemy.orm.declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
