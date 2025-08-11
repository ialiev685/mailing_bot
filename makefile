migrate:
	alembic revision --autogenerate -m "${NAME}"
	alembic upgrade head


test:
# -s чтобы срабатывал логи print 	
	pytest -s