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

Since you allow file uploads, you must add a Volume. Railway's UI has changed, so the "Volumes" tab might not be visible inside the service card.

**Method A: Context Menu (Canvas)**
1.  Go to the main project **Canvas** (where you see the connected cards).
2.  **Right-click** on your **Django App** card.
3.  Select **"Add Volume"** (or "Volume").
4.  It will appear attached to your service. Click on the Volume to configure it.
5.  Set the **Mount Path** to `/app/media`.

**Method B: Command Palette**
1.  Press `Cmd + K` (Mac) or `Ctrl + K` (Windows) to open the Command Palette.
2.  Type **"Volume"**.
3.  Select **"Volume: Add"** and choose your Django service.
4.  Configure the **Mount Path** to `/app/media`.

## Step 6: Generate Domain

## Step 6: Public Domain

1.  Click on your **Django App** card.
2.  Go to **"Settings"** -> **"Networking"**.
3.  Under **"Public Networking"**, checking if a domain is already there (e.g., `web-production-xxxx.up.railway.app`).
4.  If not, click **"Generate Domain"** or **"Custom Domain"** to create one.
5.  **Copy this URL** and update your `CSRF_TRUSTED_ORIGINS` variable in Step 4 with `https://` in front.

## Step 7: Add Custom Domain (hewor.in)

1.  In your **Django App** settings on Railway, go to **"Networking"** -> **"Public Networking"**.
2.  You likely already see `hewor.in` listed. It says **"Waiting for DNS update"**.
3.  Click the purple link **"Show instructions"** (or the small info icon).
4.  Railway will show you the exact DNS records (CNAME or A Record) you need.
5.  **Log in to Hostinger/GoDaddy** (where you bought `hewor.in`).
6.  Go to **DNS Settings**.
7.  Add the records exactly as Railway shows.
    *   **Type**: `CNAME` (usually)
    *   **Name**: `@` or `www`
    *   **Value**: `web-production-xxxx.up.railway.app` (or similar)
    *   **Name**: `@` (for hewor.in) or `www` (for www.hewor.in)
    *   **Value**: The target provided by Railway (e.g., `hewor-project.up.railway.app` or an IP address).
7.  Wait for a few minutes for changes to propagate.
8.  **Important**: Update your Railway Environment Variable `CSRF_TRUSTED_ORIGINS` to include `https://hewor.in` and `https://www.hewor.in`.

## Step 8: Redeploy

1.  Railway usually redeploys automatically when variables change.
2.  If not, click **"Deployments"** -> **"Redeploy"**.

## Troubleshooting

-   **Build Failed?** Check the "Build Logs".
-   **App Crashed?** Check the "Deploy Logs".
-   **Static Files Missing?** Ensure `Whitenoise` is configured (we already did this!).

---
**Enjoy your deployed app!** 🎉
