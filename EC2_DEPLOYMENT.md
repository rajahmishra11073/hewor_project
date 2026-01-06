# Hewor Project - Amazon EC2 Deployment Guide (Automated)

This guide details the steps to deploy the Hewor Django project to an Amazon EC2 instance using the `setup_server.sh` automation script.

## 1. Launch EC2 Instance

1.  Log in to AWS Console.
2.  Launch a new instance:
    *   **OS**: Ubuntu Server 22.04 LTS or 24.04 LTS (HVM).
    *   **Instance Type**: t2.micro (Free tier eligible) or t3.micro.
    *   **Key Pair**: Create a new key pair or use an existing one.
    *   **Security Group**: Allow **SSH (22)**, **HTTP (80)**, and **HTTPS (443)**.
3.  Launch the instance.

## 2. Deploy Using Automation Script

Connect to your instance:
```bash
ssh -i "your-key.pem" ubuntu@<your-ec2-public-ip>
```

**Run the following commands on the server:**

1.  **Download the Setup Script**:
    *(You can copy `deployment/setup_server.sh` provided in this project manually, or create it on the server)*
    
    ```bash
    # Quick way to create the script on server if you haven't pushed it yet
    nano setup_server.sh
    # Paste the content of 'deployment/setup_server.sh' here, then save (Ctrl+O, Enter, Ctrl+X)
    
    chmod +x setup_server.sh
    ```

2.  **Run the Script**:
    
    ```bash
    ./setup_server.sh https://github.com/rajahmishra11073/hewor_project.git
    ```

    *This script will install Python, MySQL, Nginx, Gunicorn, clone your code, and set up the services.*

## 3. Post-Install Configuration

After the script finishes:

1.  **Configure Secrets**:
    The script created a default `.env` file. You **MUST** edit it.
    ```bash
    nano /home/ubuntu/hewor_project/.env
    ```
    *   Set `DEBUG=False`
    *   Set a strong `SECRET_KEY`
    *   Update Database credentials if you changed them

2.  **Apply Changes**:
    ```bash
    sudo systemctl restart gunicorn
    ```

## 4. Domain & SSL

1.  **Point your Domain**: Go to your DNS provider and point `hewor.in` (A Record) to your EC2 IP address.
2.  **Enable HTTPS**:
    ```bash
    sudo certbot --nginx -d hewor.in -d www.hewor.in
    ```

