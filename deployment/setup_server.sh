#!/bin/bash

# Hewor Project - EC2 Setup Script
# Run this script on your fresh Ubuntu EC2 instance.
# Usage: ./setup_server.sh <YOUR_GITHUB_REPO_URL>

REPO_URL=$1

if [ -z "$REPO_URL" ]; then
    echo "Error: Please provide your GitHub repository URL."
    echo "Usage: ./setup_server.sh <YOUR_GITHUB_REPO_URL>"
    exit 1
fi

echo "--- Starting Server Setup ---"

# 1. Update and Install Dependencies
echo "--> Updating system packages..."
sudo apt update && sudo apt upgrade -y
echo "--> Installing Python, Git, Nginx, MySQL..."
sudo apt install python3-pip python3-dev libmysqlclient-dev nginx curl git mysql-server python3-venv -y

# 2. Database Setup (Basic)
echo "--> configuring MySQL..."
# Secure installation is interactive, so we skip it here or user does it manually.
# We will create the DB and User.
echo "Creating database 'hewor_db' and user 'hewor_user'..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS hewor_db CHARACTER SET utf8mb4;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'hewor_user'@'localhost' IDENTIFIED BY 'hewor_password_123';"
sudo mysql -e "GRANT ALL PRIVILEGES ON hewor_db.* TO 'hewor_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
echo "NOTE: Please change the database password in production!"

# 3. Clone Repository
echo "--> Cloning repository..."
cd /home/ubuntu
if [ -d "hewor_project" ]; then
    echo "Directory hewor_project already exists. Pulling latest changes..."
    cd hewor_project
    git pull
else
    git clone "$REPO_URL" hewor_project
    cd hewor_project
fi

# 4. Python Environment
echo "--> Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 5. Environment Variables
if [ ! -f ".env" ]; then
    echo "--> Creating .env file from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        touch .env
        echo "DEBUG=False" >> .env
        echo "SECRET_KEY=change_this_secret_key_in_production" >> .env
        echo "ALLOWED_HOSTS=hewor.in,www.hewor.in,localhost,127.0.0.1" >> .env
    fi
    echo "WARNING: You MUST edit configs/.env with your real secrets!"
fi

# 6. Django Setup
echo "--> Running migrations and collecting static files..."
python manage.py migrate
python manage.py collectstatic --noinput

# 7. Configure Gunicorn
echo "--> Configuring Gunicorn..."
# Adjust the path in gunicorn.service if needed, assumes /home/ubuntu/hewor_project
sudo cp deployment/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# 8. Configure Nginx
echo "--> Configuring Nginx..."
sudo cp deployment/nginx_hewor.conf /etc/nginx/sites-available/hewor
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi
sudo ln -sf /etc/nginx/sites-available/hewor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 9. SSL Setup (Certbot)
echo "--> Installing Certbot..."
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -sf /snap/bin/certbot /usr/bin/certbot

echo "----------------------------------------------------------------"
echo "SETUP COMPLETE!"
echo "----------------------------------------------------------------"
echo "What you need to do next:"
echo "1. Edit the .env file: 'nano /home/ubuntu/hewor_project/.env'"
echo "   - Change SECRET_KEY"
echo "   - Verification DB credentials"
echo "2. Restart Gunicorn: 'sudo systemctl restart gunicorn'"
echo "3. Run Certbot for HTTPS: 'sudo certbot --nginx -d hewor.in -d www.hewor.in'"
echo "----------------------------------------------------------------"
