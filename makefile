migrate:
	alembic revision --autogenerate -m "${NAME}"
	alembic upgrade head

start:
	python main.py

test:
# -s чтобы срабатывал логи print 	
	pytest -s