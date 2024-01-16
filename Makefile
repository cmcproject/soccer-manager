DJANGO = app

pre-commit:	# Run precommit
	pre-commit run --all-files

build: # Builds necessary docker images.
	docker-compose build

up: # Starts up the application server and Postgres server
	docker-compose up

down:
	docker-compose down

makemigrations:
	docker-compose run --rm $(DJANGO) sh -c "python manage.py makemigrations"

migrate:
	docker-compose run --rm $(DJANGO) sh -c "python manage.py migrate"

lock:
	docker-compose run --rm $(DJANGO) sh -c "poetry lock"

tests:
	docker-compose run --rm $(DJANGO) sh -c "pytest ."

startapp $(app_name):
	docker-compose run --rm $(DJANGO) sh -c "python manage.py startapp $(app_name)"

createsuperuser:
	docker-compose run --rm $(DJANGO) sh -c "python manage.py createsuperuser"
