from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database import get_db  # Импортируем функцию для создания и закрытия сессии
from .. import models, schemas  # Импортируем модели БД
import dateutil.parser  # для преобразования строк в формате даты и времени в объекты datetime
import requests  # для выполнения HTTP-запросов
from typing import List, Optional

router = APIRouter(
    prefix='/items',
    tags=['Questions']
)


# Создаем функцию принимающую количество вопросов,
# которые мы хотим получить, и возвращает ответ от API в формате JSON.
def get_questions(count: int):
    response = requests.get(f"https://jservice.io/api/random?count={count}")
    return response.json()


# Маршрут GET для получения всех вопросов или поиска по совпадению
@router.get("/results", response_model=List[schemas.QuestionOut])
def get_all_questions(db: Session = Depends(get_db),
                      limit: int = 10, skip: int = 0, search: str = ""):
    questions = db.query(models.QuizQuestion).filter(
        models.QuizQuestion.question_text.contains(search)).limit(limit).offset(skip).all()
    return questions


# Маршрут GET для получения последнего добавленного вопроса
@router.get("/")
def get_last_question(db: Session = Depends(get_db)):
    # Получаем последний добавленный вопрос
    last_question = db.query(models.QuizQuestion).order_by(models.QuizQuestion.id.desc()).first()

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
@router.get("/{id}")
def get_question_by_id(id: int,
                       db: Session = Depends(get_db)):
    # Получаем вопрос по его порядковому номеру
    question = db.query(models.QuizQuestion).filter(models.QuizQuestion.id == id).first()

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
        return {"detail": f"Question with id {id} does not exist"}


# Маршурт DELETE для удаления вопроса по ID
@router.delete("/{id}")
def delete_question(id: int,
                    db: Session = Depends(get_db)):
    # Получаем вопрос по его порядковому номеру
    question = db.query(models.QuizQuestion).filter(models.QuizQuestion.id == id).first()
    if question is None:
        return {"detail": f"Question with id {id} does not exist"}  # Если вопрос с указанным ID не найден
    db.delete(question)  # Удаляем вопрос
    db.commit()  # Сохраняем изменения
    return {"detail": f"Question with id {id} deleted"}  # Возвращаем сообщение об успешном удалении


# Маршрут POST для создания новых вопросов. Пример POST запроса {"questions_num": 5}
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.Item,
                db: Session = Depends(get_db)):

    for _ in range(item.questions_num):
        for attempt in range(5):  # Ограничиваем количество попыток
            response = get_questions(1)  # Получаем один вопрос из API
            question = response[0]  # API возвращает список, забираем первый элемент

            # Проверяем есть ли вопрос в базе
            existing_question = db.query(models.QuizQuestion).filter(models.QuizQuestion.id == question['id']).first()

            if existing_question is None:  # Если вопроса еще нет в базе данных
                # преобразуем строку даты в объект datetime
                created_at = dateutil.parser.parse(question['created_at'])

                # Создаем новый объект для передачи в базу
                quiz_question = models.QuizQuestion(
                    id=question['id'],
                    question_text=question['question'],
                    answer_text=question['answer'],
                    created_at=created_at
                )

                # Добавляем новый объект в сессию
                db.add(quiz_question)

                # Сохраняем все изменения
                db.commit()

                break  # Выходим из внутреннего цикла, переходим к следующему вопросу
        else:  # Если после 5 попыток мы не нашли уникальный вопрос
            break  # Выходим из внешнего цикла, прекращаем поиск вопросов

    return {"detail": "Questions saved"}
