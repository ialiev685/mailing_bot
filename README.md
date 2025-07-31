1. Собрать приложение

sudo docker-compose up --build -d - собрать приложение

sudo docker-compose build --no-cache && sudo docker-compose up -d - cобрать без кэша

2. Миграции

alembic revision --autogenerate -m "Описание" - ревизия и действие миграций
alembic upgrade head - применение миграций

или

make migrate NAME='Описание'

2. Создать БД

docker exec -it container_name psql -U user -d postgres или если через docker терминал - psql -U user -d postgres
user - имя юзера при создании контейнеров
container_name - имя запущенные
postgres - имя базы данных по умолчанию

в терминале введите:
CREATE DATABASE name_db; - создание новой бд с необходимым названием (например name_db)
\q - выход

Памятка:

pip freeze > requirements.txt - запись зависимостей

pip install -r requirements.txt - установка зависимостей
