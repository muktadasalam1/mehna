# Mehna — Docker Setup Guide

Run the full Mehna stack (Flask app + PostgreSQL) in Docker containers.

---

## Prerequisites

### Linux / Arch / Manjaro

```bash
# Arch / Manjaro
sudo pacman -S docker docker-compose

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group (log out and back in after this)
sudo usermod -aG docker $USER
```

### Windows

1. Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
2. Make sure **WSL 2** is enabled (Docker Desktop will prompt you)
3. After install, open PowerShell and verify:
   ```powershell
   docker --version
   docker compose version
   ```

> **Note for Windows users:** This guide uses `docker compose` (v2 syntax). On older Docker Desktop installs you may need `docker-compose` with a hyphen. Both work; if one fails, try the other.

---

## First-Time Setup

From the **project root** (`mehna/`):

### 1. Create your environment file

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```
DATABASE_URL=postgresql://postgres:123@db:5432/mehna_db
SECRET_KEY=change-me-in-production
```

### 2. Start the full stack

```bash
cd compose
docker compose up -d --build
```

This will:
- Build the Flask app image (multi-stage, Python 3.12-slim)
- Pull the `postgres:17-alpine` image
- Create the `mehna_db` database
- Load `init.sql` (schema + seed data)
- Start the Flask app on port **5000**

### 3. Verify everything is running

```bash
docker compose ps
```

You should see both `mehna_db` (healthy) and `mehna_app` (running).

### 4. Access the app

```
http://localhost:5000
```

| Role | Email | Password |
|------|-------|----------|
| Employer (Admin) | employer@mehna.com | 123456 |
| Job Seeker | seeker@mehna.com | 123456 |

---

## Development Mode

The default setup mounts your source code into the container. Changes to Python files are reflected without rebuilding.

### Enable debug mode (auto-reload)

```bash
# In the project root .env
FLASK_DEBUG=1
```

Then restart:

```bash
cd compose
docker compose restart app
```

### Rebuild after dependency changes

If you modify `requirements.txt`, rebuild the image:

```bash
cd compose
docker compose up -d --build app
```

---

## Daily Development Commands

### Start / Stop

```bash
cd compose

# Start (in background)
docker compose up -d

# Stop (data is preserved in the volume)
docker compose down

# Stop and DELETE all data (resets DB to init.sql)
docker compose down -v
docker compose up -d --build
```

### View Logs

```bash
cd compose

# Follow all logs
docker compose logs -f

# App logs only
docker compose logs -f app

# DB logs only
docker compose logs -f db

# Last 50 lines
docker compose logs --tail 50 app
```

### Connect to PostgreSQL Directly

```bash
# Using psql inside the container
docker compose exec db psql -U postgres mehna_db

# Using your local psql (must be installed)
psql -h localhost -U postgres -d mehna_db
```

### Check Database Contents

```sql
-- List tables
\dt

-- Count users
SELECT COUNT(*) FROM users;

-- List all companies
SELECT id, name, verification_status FROM companies;

-- Exit psql
\q
```

---

## Useful Docker Commands

| Command | What it does |
|---------|-------------|
| `docker compose ps` | List running containers |
| `docker compose up -d` | Start in detached mode |
| `docker compose up -d --build` | Rebuild and start |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | Stop, remove containers + **delete data** |
| `docker compose logs -f app` | Tail Flask app logs |
| `docker compose logs -f db` | Tail PostgreSQL logs |
| `docker compose restart app` | Restart the Flask app |
| `docker compose exec db bash` | Shell into the DB container |
| `docker compose exec app bash` | Shell into the app container |
| `docker volume ls` | List Docker volumes |
| `docker system prune` | Clean up unused Docker resources |

---

## Resetting the Database

If you need a fresh start (e.g., schema changed):

```bash
cd compose
docker compose down -v        # destroy volume
docker compose up -d --build  # re-create from init.sql
```

---

## Updating init.sql

If the schema changes and you need to re-export from a running PostgreSQL:

```bash
# Dump from Docker
docker compose exec db pg_dump -U postgres mehna_db > compose/init.sql
```

Then restart the container to apply:

```bash
cd compose
docker compose down -v
docker compose up -d --build
```

---

## Troubleshooting

### Port 5000 already in use

Another process is occupying the port. Find and stop it:

```bash
# Linux / Arch
lsof -i :5000
kill <PID>
```

### Port 5432 already in use

A local PostgreSQL installation may be occupying the port.

```bash
# Linux / Arch
sudo systemctl stop postgresql
```

### App container keeps restarting

Check logs for errors:

```bash
docker compose logs app
```

Common causes:
- DB is not ready yet — the app has `depends_on` with health check, but if it still fails, wait a few seconds and check again
- `DATABASE_URL` uses `localhost` instead of `db` — ensure `.env` has `@db:` not `@localhost:`

### Permission denied on Linux

```bash
sudo usermod -aG docker $USER
# Log out and log back in, then try again
```

### Windows path issues

Make sure you run all commands from the project root or `compose/` directory. Paths in `docker-compose.yml` are relative to where you run the command.

### Reset everything

```bash
cd compose
docker compose down -v
docker compose up -d --build
```

---

## File Overview

```
mehna/
├── Dockerfile               # Flask app container definition
├── .dockerignore            # Files excluded from Docker build
├── .env.example             # Environment variable template
├── compose/
│   ├── docker-compose.yml   # Full stack: Flask app + PostgreSQL
│   ├── init.sql             # DB schema + seed data (auto-runs on first start)
│   └── README.md            # This file
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:123@db:5432/mehna_db` | PostgreSQL connection string |
| `SECRET_KEY` | `change-me-in-production` | Flask secret key for sessions |
| `DB_PASSWORD` | `123` | PostgreSQL password |
| `FLASK_DEBUG` | `0` | Set to `1` to enable debug mode |
| `PORT` | `5000` | Flask app port |

> **Important:** When using Docker, `DATABASE_URL` must point to `db` (the service name) instead of `localhost`. The `.env.example` already has the correct value.
