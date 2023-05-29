# Импортируем необходимые компоненты из библиотеки SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base


# Определяем класс QuizQuestion, который описывает структуру таблицы в БД
class QuizQuestion(Base):
    __tablename__ = "quiz_questions"  # Имя таблицы в БД
    # Описываем столбцы таблицы:
    id = Column(Integer, primary_key=True, index=True)  # ID вопроса (целочисленное значение, первичный ключ, индексированный)
    question_text = Column(String, index=True)  # Текст вопроса (строковое значение, индексированный)
    answer_text = Column(String, index=True)  # Текст ответа (строковое значение, индексированный)
    created_at = Column(DateTime(timezone=True))  # Дата создания вопроса (тип данных DateTime с учетом временной зоны)
