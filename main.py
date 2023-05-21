from fastapi import FastAPI
from models import QuizQuestion  # импорт модели вопроса из файла models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import requests  # для выполнения HTTP-запросов
import dateutil.parser  # для преобразования строк в формате даты и времени в объекты datetime

# Создаем экземпляр приложения FastAPI
app = FastAPI()

# Создаем подключение к базе данных
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Описываем модель запроса
class Item(BaseModel):
    questions_num: int


# Создаем функцию принимающую количество вопросов,
# которые мы хотим получить, и возвращает ответ от API в формате JSON.
def get_questions(count: int):
    response = requests.get(f"https://jservice.io/api/random?count={count}")
    return response.json()


# Маршрут GET для получения последнего добавленного вопроса
@app.get("/items/")
def get_last_question():
    # Создаем сессию для работы с базой данных
    session = SessionLocal()

    # Получаем последний добавленный вопрос
    last_question = session.query(QuizQuestion).order_by(QuizQuestion.id.desc()).first()

    session.close()  # Закрываем сессию

    # Проверяем нашелся ли вопрос
    if last_question is not None:
        # Возвращаем вопрос в формате JSON
        return {
            "id": last_question.id,
            "question_text": last_question.question_text,
            "answer_text": last_question.answer_text,
            "created_at": str(last_question.created_at)  # преобразуем datetime в строку для ответа
        }
    else:
        # В случае, если вопросов нет, возвращаем пустой объект
        return {}


# Маршрут GET для получения вопроса по его ID
@app.get("/items/{id}")
def get_question_by_id(id: int):
    # Создаем сессию для работы с базой данных
    session = SessionLocal()

    # Получаем вопрос по его порядковому номеру
    question = session.query(QuizQuestion).order_by(QuizQuestion.id).offset(id - 1).first()

    session.close()  # Закрываем сессию

    # Проверяем нашелся ли вопрос
    if question is not None:
        # Возвращаем вопрос в формате JSON
        return {
            "id": question.id,
            "question_text": question.question_text,
            "answer_text": question.answer_text,
            "created_at": str(question.created_at)  # преобразуем datetime в строку для ответа
        }
    else:
        # В случае, если вопроса с таким id нет, возвращаем сообщение об ошибке
        return {"ID": "Does not exist"}


# Маршурт DELETE для удаления вопроса по ID
@app.delete("/items/{id}")
def delete_question(id: int):
    session = SessionLocal()  # Создаем сессию для работы с базой данных
    # Получаем вопрос по его порядковому номеру
    question = session.query(QuizQuestion).filter(QuizQuestion.id == id).first()
    if question is None:
        session.close()  # Закрываем сессию
        return {"detail": f"Question with id {id} does not exist"}  # Если вопрос с указанным ID не найден
    session.delete(question)  # Удаляем вопрос
    session.commit()  # Сохраняем изменения
    session.close()  # Закрываем сессию
    return {"detail": f"Question with id {id} deleted"}  # Возвращаем сообщение об успешном удалении


# Маршрут POST для создания новых вопросов. Пример POST запроса {"questions_num": 5}
@app.post("/items/")
def create_item(item: Item):
    # Создаем сессию для работы с базой данных
    session = SessionLocal()
    QuizQuestion.metadata.create_all(bind=engine)
    for _ in range(item.questions_num):
        for attempt in range(5):  # Ограничиваем количество попыток
            response = get_questions(1)  # Получаем один вопрос из API
            question = response[0]  # API возвращает список, забираем первый элемент

            # Проверяем есть ли вопрос в базе
            existing_question = session.query(QuizQuestion).filter(QuizQuestion.id == question['id']).first()

            if existing_question is None:  # Если вопроса еще нет в базе данных
                # преобразуем строку даты в объект datetime
                created_at = dateutil.parser.parse(question['created_at'])

                # Создаем новый объект для передачи в базу
                quiz_question = QuizQuestion(
                    id=question['id'],
                    question_text=question['question'],
                    answer_text=question['answer'],
                    created_at=created_at
                )

                # Добавляем новый объект в сессию
                session.add(quiz_question)

                # Сохраняем все изменения
                session.commit()

                break  # Выходим из внутреннего цикла, переходим к следующему вопросу
        else:  # Если после 5 попыток мы не нашли уникальный вопрос
            break  # Выходим из внешнего цикла, прекращаем поиск вопросов

        session.close()  # Закрываем сессию

    return {"detail": "Questions saved"}
