# 🚀 Complete Deployment Roadmap: AWS EC2 + Hostinger Domain
**Project:** Hewor (`hewor.in`)  
**Stack:** Django + Nginx + Gunicorn + MySQL + Ubuntu 22.04  

This guide covers everything from buying the domain to having a secure, live website.

---

## 🟢 PHASE 1: AWS Infrastructure Setup

### 1. Create an AWS Account
*   Go to [aws.amazon.com](https://aws.amazon.com) and sign up.
*   You will need a credit/debit card for verification (you get 12 months free tier).

### 2. Launch an EC2 Instance (Virtual Server)
1.  **Login** to AWS Console > Search for **EC2**.
2.  Click **Launch Instance**.
3.  **Name**: `Hewor-Server`
4.  **OS Image**: Select **Ubuntu** (Choose Server 22.04 LTS or 24.04 LTS).
5.  **Instance Type**: Select **t2.micro** (Free Tier Eligible).
6.  **Key Pair (Login Key)**:
    *   Click "Create new key pair".
    *   Name: `hewor-key`
    *   Type: **RSA**
    *   Format: **.pem** (for Mac/Linux)
    *   **Download connection key** and keep it safe! (e.g., in your project folder).
7.  **Network Settings**:
    *   Check: **Allow SSH traffic from Anywhere** (0.0.0.0/0).
    *   Check: **Allow HTTP traffic from the internet**.
    *   Check: **Allow HTTPS traffic from the internet**.
8.  Click **Launch Instance**.

### 3. Get a Static IP (Elastic IP)
*Crucial Step: Standard AWS IPs change if you restart the server. An Elastic IP stays forever.*

1.  In EC2 Dashboard left menu, go to **Network & Security** > **Elastic IPs**.
2.  Click **Allocate Elastic IP address** > **Allocate**.
3.  Select the new IP address from the list.
4.  Click **Actions** > **Associate Elastic IP address**.
5.  **Instance**: Select your `Hewor-Server`.
6.  Click **Associate**.
7.  **COPY THIS IP ADDRESS.** (We will call this `<YOUR-EC2-IP>`).

---

## 🔵 PHASE 2: Hostinger Domain Setup

### 1. Buy the Domain
1.  Go to [Hostinger.in](https://www.hostinger.in).
2.  Search for `hewor.in` and buy it.

### 2. Point Domain to AWS (DNS Configuration)
1.  Log in to Hostinger Dashboard.
2.  Go to **Domains** > Manage `hewor.in`.
3.  Look for **DNS / Name Servers** in the sidebar.
4.  **Delete** any default "A" records or "CNAME" records that point to Hostinger parking pages.
5.  **Add New Records**:

    | Type | Name | Points to (Value) | TTL |
    | :--- | :--- | :--- | :--- |
    | **A** | `@` | `<YOUR-EC2-IP>` | 3600 |
    | **CNAME** | `www` | `hewor.in` | 3600 |

    *(Replace `<YOUR-EC2-IP>` with the Elastic IP involved in Phase 1).*

    > **Note:** DNS propagation can take 10 minutes to 24 hours.

---

## 🟠 PHASE 3: Server Deployment

### 1. Prepare your Local Key
Open your terminal on your Mac.

```bash
cd /path/to/where/you/downloaded/key
# Make the key secure (AWS requires this)
chmod 400 hewor-key.pem
```

### 2. Connect to the Server
```bash
ssh -i "hewor-key.pem" ubuntu@<YOUR-EC2-IP>
```
*Type `yes` if asked about authenticity.*

### 3. Run the Automated Setup
I have prepared a script that installs everything (Python, Nginx, Database, etc.) for you.

**Run these commands inside the server terminal:**

```bash
# 1. Download the script
curl -O https://raw.githubusercontent.com/rajahmishra11073/hewor_project/main/deployment/setup_server.sh

# 2. Make it executable
chmod +x setup_server.sh

# 3. Run it (This takes about 5 minutes)
./setup_server.sh https://github.com/rajahmishra11073/hewor_project.git
```

---

## 🟣 PHASE 4: Final Configuration

### 1. Configure Secrets (On Server)
The script creates a generic `.env` file. You need to update it.

```bash
nano ~/hewor_project/.env
```
*   Change `DEBUG=True` to `DEBUG=False`
*   Change `ALLOWED_HOSTS` to `hewor.in,www.hewor.in,<YOUR-EC2-IP>`
*   (Optional) Update Database password if you secured MySQL manually.

*Save and Exit: Ctrl+O, Enter, Ctrl+X*

### 2. Restart Services
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### 3. Secure with HTTPS (SSL)
Enable the green lock icon using Certbot:

```bash
sudo certbot --nginx -d hewor.in -d www.hewor.in
```
*   Enter your email.
*   Agree to terms.
*   Select "Regular" if asked about redirect.

---

## ✅ DONE!
Visit **https://hewor.in**, and your site should be live!
