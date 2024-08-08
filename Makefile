mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

celery:
	celery -A core worker -l INFO

beat:
	celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

flower:
	celery -A core.celery.app flower --port=5001

dumpdata:
	python3 manage.py dumpdata --indent=2 apps.Category > categories.json

loaddata:
	python3 manage.py loaddata categories # products

image:
	docker build -t django_image .

container:
	docker run --name django_container -p 8000:8000 -d django_image
compose:
	docker compose up