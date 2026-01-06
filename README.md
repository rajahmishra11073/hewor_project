# Hewor Project

A Django-based web application for freelance service management.

## Prerequisites

- **Python**: 3.10+ (Tested on 3.13)
- **Database**: MySQL or MariaDB

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd hewor_project
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Environment Variables

Create a `.env` file in the root directory and configure the following keys. 

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DEBUG` | Set `True` for local dev, `False` for production | `False` |
| `SECRET_KEY` | Critical security key for Django | *Required for Prod* |
| `ALLOWED_HOSTS` | Comma-separated list of domains | `127.0.0.1,localhost` |
| `DB_NAME` | MySQL/MariaDB Database Name | `hewor_db` |
| `DB_USER` | Database User | `root` |
| `DB_PASSWORD` | Database Password | *(Empty)* |
| `DB_HOST` | Database Host | `127.0.0.1` |
| `DB_PORT` | Database Port | `3306` |
| `SECURE_SSL_REDIRECT`| Force HTTPS (Set `True` in Prod) | `False` |
| `SESSION_COOKIE_SECURE`| Secure cookies (Set `True` in Prod) | `False` |
| `CSRF_COOKIE_SECURE`| Secure CSRF cookies (Set `True` in Prod)| `False` |

## Local Development

1.  **Apply Migrations:**
    ```bash
    python manage.py migrate
    ```

2.  **Create Superuser:**
    ```bash
    python manage.py createsuperuser
    ```

3.  **Run Server:**
    ```bash
    python manage.py runserver
    ```

## Testing

Run the integration test suite to verify authentication flows:

```bash
python manage.py test core
```

## Deployment (Heroku/PaaS)

This project is configured with a `Procfile` using **Gunicorn** and **Whitenoise** for static files.

1.  **Heroku Setup:**
    ```bash
    heroku create your-app-name
    ```

2.  **Configure Environment:**
    Set all variables listed in the Environment Variables section using `heroku config:set KEY=VALUE`.

3.  **Deploy:**
    ```bash
    git push heroku main
    ```

4.  **Post-Deployment:**
    ```bash
    heroku run python manage.py migrate
    ```
