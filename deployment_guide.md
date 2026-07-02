# VM Deployment Guide for Meeting Task Manager

This guide covers everything you need to deploy your `meetingtask-manager` on a fresh Ubuntu VM. 

> [!WARNING]
> **Secret Exposure Notice**: The ChatGPT conversation you shared contained real secrets (`DATABASE_URL` password, `SECRET_KEY`, and `AZURE_OPENAI_API_KEY`). **You must rotate (change) these credentials immediately** in your production environment to prevent unauthorized access.

## Step 0: Fix the Repository First

The root cause of the backend failing to start is the corrupted Alembic migration history, as diagnosed in your conversation. I have already fixed this in your local workspace by:
1. Updating `backend/alembic/env.py` to import all models (including `RefreshToken` and `Notification`).
2. Deleting the corrupted migration files in `backend/alembic/versions/`.

Before proceeding to your VM, you need to push these changes to GitHub:

```bash
git add backend/alembic/env.py
git add backend/alembic/versions/
git commit -m "Fix: Remove corrupted migrations and update env.py imports"
git push origin main
```

---

## Step 1: VM Preparation

SSH into your fresh Ubuntu VM and run the following commands to install dependencies:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Git and Nginx
sudo apt install -y git nginx

# Install Docker
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

# Install Docker Compose (V2 plugin)
sudo apt install -y docker-compose-v2
```

> [!NOTE]
> After running `usermod`, log out of the VM and log back in so the group changes take effect, allowing you to run `docker` commands without `sudo`.

---

## Step 2: Clone the Repository

Clone your repository into the VM:

```bash
cd ~
git clone https://github.com/pathaxiom-menntr/meetingtask-manager.git
cd meetingtask-manager
```

---

## Step 3: Set up Environment Variables

Create the required environment file for Docker.

```bash
nano .env.docker
```

Paste the following (replacing the placeholder values and using **new** secrets):

```env
# Backend Database (Ensure POSTGRES_PASSWORD matches DATABASE_URL)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_new_secure_db_password
POSTGRES_DB=meeting_task_manager

# Backend FastAPI settings
DATABASE_URL=postgresql://postgres:your_new_secure_db_password@db:5432/meeting_task_manager
SECRET_KEY=your_new_secure_random_string_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS="http://your-vm-ip-or-domain"

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_new_azure_key
AZURE_OPENAI_ENDPOINT=https://menntr-openai.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt4-interview
```

Update your `docker-compose.yml` on the VM to make sure it loads `.env.docker`. Usually, Docker Compose reads from `.env` by default, so you can just symlink or rename it:

```bash
cp .env.docker .env
```

---

## Step 4: Generate the Initial Migration

Since we deleted the corrupted migrations, we need to generate a fresh initial migration from your SQLAlchemy models. We will do this directly inside the Docker container.

1. First, build the images and start **only the database container** so Alembic has an empty DB to connect to:
   ```bash
   docker compose build --no-cache
   docker compose up -d db
   ```

2. Wait a few seconds for PostgreSQL to become healthy.

3. Generate the initial schema migration (bypassing the entrypoint so it doesn't crash trying to run nonexistent migrations):
   ```bash
   docker compose run --rm --entrypoint "" backend alembic revision --autogenerate -m "Initial schema"
   ```

   *You should see output indicating that Alembic detected your tables and created a new revision file in `backend/alembic/versions/`.*

---

## Step 5: Start the Application

Now that the initial migration exists, you can start the entire stack. The entrypoint script (`entrypoint.sh`) will automatically run `alembic upgrade head` and create all tables in the database.

```bash
docker compose up -d
```

Check the logs to ensure both frontend and backend started successfully:

```bash
docker compose logs -f
```

---

## Step 6: Setup Nginx Reverse Proxy

To make your application accessible over the standard web ports (80) and route traffic properly to the frontend and backend containers, configure Nginx.

Create a new Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/meetingtask-manager
```

Paste the following configuration (replace `YOUR_VM_IP_OR_DOMAIN` with your actual IP or domain name):

```nginx
server {
    listen 80;
    server_name YOUR_VM_IP_OR_DOMAIN;

    # Route requests to /api/ to the backend (FastAPI) on port 8000
    location /api/ {
        # Strip the /api prefix before forwarding if your FastAPI app doesn't expect it
        # Or just proxy directly depending on your API route prefix setup
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Route all other requests to the frontend (Next.js) on port 3000
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration and restart Nginx:

```bash
# Remove the default site
sudo rm /etc/nginx/sites-enabled/default

# Enable your new site
sudo ln -s /etc/nginx/sites-available/meetingtask-manager /etc/nginx/sites-enabled/

# Test the Nginx configuration for syntax errors
sudo nginx -t

# Restart Nginx to apply changes
sudo systemctl restart nginx
```

> [!TIP]
> **HTTPS / SSL Configuration**
> If you have a domain name pointing to your VM, you can easily secure it with a free SSL certificate using Certbot:
> ```bash
> sudo apt install certbot python3-certbot-nginx
> sudo certbot --nginx -d your-domain.com
> ```

---

## Step 7: Verify the Deployment

1. **Frontend:** Open `http://YOUR_VM_IP_OR_DOMAIN` in your browser. You should see your Next.js application.
2. **Backend Docs:** Open `http://YOUR_VM_IP_OR_DOMAIN/api/docs` (or `http://YOUR_VM_IP:8000/docs` directly if you haven't closed the firewall port 8000) to verify FastAPI is running and connected to the DB.
