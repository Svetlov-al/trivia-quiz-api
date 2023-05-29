# Trivia Quiz API

Этот проект представляет собой API для создания, получения и удаления викторинных вопросов. Он написан на Python с использованием FastAPI и SQLAlchemy для взаимодействия с базой данных PostgreSQL. Все вопросы получаются из внешнего API на сайте **_jservice.io_**.

### Установка

Для запуска этого приложения вам потребуется Docker. Клонируйте репозиторий и запустите docker-compose up в корневой директории проекта.

Использование
API предоставляет следующие маршруты:

### GET /items/results - получить список вопросов из базы данных.
Так же по данному маршруту можно использовать параметры для фильтрации вопросов по ключевым словам в поле question_text,
ограничивать количество вопросов на странице (limit=10), и так же offset(default=0) для пагинации.


### GET /items/ - получить последний добавленный в базу данных вопрос.


### GET /items/{id} - получить вопрос по его ID.

Индивидуальный ID вопроса можно получить из ответа на запрос GET /items/results.

### DELETE /items/{id} - удалить вопрос по его ID.

При запросе нужно указать уникальный ID вопроса.

### POST /items/ - создать новые вопросы. 
Запрос должен содержать JSON-объект с одним полем questions_num, которое указывает количество вопросов, которые нужно создать.

### Пример запроса:

{

####     "questions_num": 5

}

При успешном создании вопросов API вернет JSON-объект с одним полем {"detail": "Questions saved"}.