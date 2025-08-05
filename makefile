migrate:
	alembic revision --autogenerate -m "${NAME}"
	alembic upgrade head


test:
	pytest