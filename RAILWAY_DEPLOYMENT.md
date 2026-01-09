# Railway.app Deployment Guide 🚀

This guide will help you deploy your Django project to Railway.app in less than 15 minutes.

## Prerequisites

1.  **GitHub Account**: Ensure your project is pushed to GitHub.
2.  **Railway Account**: Sign up at [railway.app](https://railway.app/) using your GitHub account.

## Step 1: Create a Project on Railway

1.  Log in to your Railway Dashboard.
2.  Click **"New Project"**.
3.  Select **"Deploy from GitHub repo"**.
4.  Select your repository (`hewor_project`).
5.  Click **"Deploy Now"**.

## Step 2: Add MySQL Database

1.  Once the project is created, click the **"New"** button (top right or on the canvas).
2.  Select **"Database"** -> **"Add MySQL"**.
3.  Railway will take a minute to spin up a MySQL service.

## Step 3: Connect Django to MySQL

1.  Click on the newly created **MySQL** card.
2.  Go to the **"Variables"** tab.
3.  You will see variables like `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLHOST`, `MYSQLPORT`, `MYSQLDATABASE`.
4.  Copy these values.

## Step 4: Configure Environment Variables

1.  Click on your **Django App** card (it might be called `hewor_project` or `web`).
2.  Go to the **"Variables"** tab.
3.  Add the following variables (use the values from Step 3 + your own secrets):

    | Variable Name | Value |
    | :--- | :--- |
    | `DEBUG` | `False` |
    | `NIXPACKS_PYTHON_VERSION` | `3.12` |
    | `SECRET_KEY` | *(Create a long random string)* |
    | `ALLOWED_HOSTS` | `*` |
    | `CSRF_TRUSTED_ORIGINS` | `https://your-project-url.up.railway.app` (Get this from the Settings tab later) |
    | `DB_NAME` | *(Value of MYSQLDATABASE from Step 3)* |
    | `DB_USER` | *(Value of MYSQLUSER from Step 3)* |
    | `DB_PASSWORD` | *(Value of MYSQLPASSWORD from Step 3)* |
    | `DB_HOST` | *(Value of MYSQLHOST from Step 3)* |
    | `DB_PORT` | *(Value of MYSQLPORT from Step 3)* |
    | `FIREBASE_ADMIN_CREDENTIALS` | *(Create a JSON string of your `firebase-adminsdk.json` content)* |

## Step 5: Persistent Storage (Volumes)

Since you allow file uploads, you must add a Volume.

1.  Click on your **Django App** card.
2.  Go to the **"Volumes"** tab.
3.  Click **"Add Volume"**.
4.  Mount Path: `/home/ubuntu/hewor_project/media` (or `/app/media` depending on buildpack, try `/app/media` first if using Nixpacks).
    *   *Note: Railway's default buildpath is usually `/app`. So try `/app/media`.*

## Step 6: Generate Domain

1.  Click on your **Django App** card.
2.  Go to **"Settings"** -> **"Networking"**.
3.  Click **"Generate Domain"**.
4.  It will give you a URL (e.g., `web-production-1234.up.railway.app`).
5.  Copy this URL and update your `CSRF_TRUSTED_ORIGINS` variable in Step 4 with `https://` in front.

## Step 7: Redeploy

1.  Railway usually redeploys automatically when variables change.
2.  If not, click **"Deployments"** -> **"Redeploy"**.

## Troubleshooting

-   **Build Failed?** Check the "Build Logs".
-   **App Crashed?** Check the "Deploy Logs".
-   **Static Files Missing?** Ensure `Whitenoise` is configured (we already did this!).

---
**Enjoy your deployed app!** 🎉
