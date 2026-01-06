# Deployment Guide for Hewor Project

This project is configured for deployment on Platform-as-a-Service (PaaS) providers like **Heroku**, **Render**, or **Railway**.

## Prerequisites

Ensure your deployment environment supports:
- **Python 3.10+**
- **MySQL/MariaDB** database (or PostgreSQL if you switch the driver)

## Environment Variables

You **MUST** set the following environment variables in your production environment. The application will not run securely without them.

| Variable | Description | Example Value |
| :--- | :--- | :--- |
| `SECRET_KEY` | A long, random string. **Critical for security.** | `django-insecure-ExAmPlE...` |
| `DEBUG` | Must be `False` in production. | `False` |
| `ALLOWED_HOSTS` | Comma-separated list of domains. | `hewor.herokuapp.com,hewor.com` |
| `DB_NAME` | Database name. | `hewor_db` |
| `DB_USER` | Database username. | `hewor_user` |
| `DB_PASSWORD` | Database password. | `supersecretpassword` |
| `DB_HOST` | Database hostname. | `us-cdbr-east-06.cleardb.net` |
| `DB_PORT` | Database port. | `3306` |
| `SECURE_SSL_REDIRECT` | Force HTTPS. | `True` |
| `SESSION_COOKIE_SECURE` | Secure cookies over HTTPS. | `True` |
| `CSRF_COOKIE_SECURE` | Secure CSRF cookies over HTTPS. | `True` |
| `FIREBASE_ADMIN_CREDENTIALS` | Content of `firebase-adminsdk.json` as a single line string. | `{"type": "service_account", ...}` |

## Deployment Steps

py
### Heroku (Example)

1.  **Login to Heroku**:
    ```bash
    heroku login
    ```

2.  **Create App**:
    ```bash
    heroku create hewor-app
    ```

3.  **Add Database**:
    ```bash
    heroku addons:create jawsdb:kitefin  # Or clearDB
    ```

4.  **Set Environment Variables**:
    ```bash
    heroku config:set SECRET_KEY='your-generated-secret-key'
    heroku config:set DEBUG='False'
    # ... set the rest of the variables
    ```

5.  **Deploy**:
    ```bash
    git push heroku main
    ```

6.  **Run Migrations**:
    ```bash
    heroku run python manage.py migrate
    ```

7.  **Create Superuser**:
    ```bash
    heroku run python manage.py createsuperuser
    ```

## Static Files

This project uses **WhiteNoise** to serve static files efficiently in production. The `collectstatic` command triggers automatically during the build process.
