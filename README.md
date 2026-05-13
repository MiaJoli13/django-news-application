# Django News Application (Capstone)

A Django + Django REST Framework news platform with JWT authentication, role-based permissions, article approval workflow, newsletters, and automated tests.

## Features

- Custom user model with roles:
  - `reader`
  - `journalist`
  - `editor`
- Articles with approval status
- Publishers and newsletters
- JWT authentication (`/api/token/`, `/api/token/refresh/`)
- Role-based API permissions:
  - Reader: view only
  - Journalist: create and edit own articles
  - Editor: approve and delete articles
- Article approval endpoint: `POST /api/approved/`
- Approval email notification (console backend in development)
- Unit/API tests

## Tech Stack

- Python 3
- Django 6
- Django REST Framework
- SimpleJWT
- SQLite (default in this repo)
- MySQL support via `mysqlclient`

## Project Structure

- `config/` — Django project settings and URL configuration
- `newsapp/` — app models, serializers, views, URLs, tests
- `manage.py`

## Setup

1. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Create superuser:

```bash
python manage.py createsuperuser
```

5. Run server:

```bash
python manage.py runserver
```

## API Endpoints

- Admin: `http://127.0.0.1:8000/admin/`
- Articles: `http://127.0.0.1:8000/api/articles/`
- Publishers: `http://127.0.0.1:8000/api/publishers/`
- Newsletters: `http://127.0.0.1:8000/api/newsletters/`
- JWT Token: `http://127.0.0.1:8000/api/token/`
- JWT Refresh: `http://127.0.0.1:8000/api/token/refresh/`
- Approve Article: `http://127.0.0.1:8000/api/approved/`

## Demo Users

Seeded demo users (password for all: `DemoPass123!`):

- `reader_demo`
- `journalist_demo`
- `editor_demo`

## Tests

Run tests:

```bash
python manage.py test
```

Current status: all tests passing.

## Notes

- In development, approval email output is printed to console (`EMAIL_BACKEND = console`).
- Keep secrets out of version control for production.
