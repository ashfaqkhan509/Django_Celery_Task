PROJECT_NAME=CeleryProject

# Build containers without starting them
build:
	docker compose build

# Start services without rebuilding
start:
	docker compose up

# Build and start
up:
	docker compose up --build

# Stop all services
down:
	docker compose down

# Restart services (rebuild)
restart:
	docker compose down
	docker compose up --build

# View logs
logs:
	docker compose logs -f

# Open a shell in each service
web-shell:
	docker compose exec web sh

celery-shell:
	docker compose exec celery sh

beat-shell:
	docker compose exec beat sh

# Django management commands
migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

createsuperuser:
	docker compose exec web python manage.py createsuperuser

collectstatic:
	docker compose exec web python manage.py collectstatic --noinput

# Show container status
ps:
	docker compose ps

# Remove everything and prune
clean:
	docker compose down -v
	docker system prune -af --volumes