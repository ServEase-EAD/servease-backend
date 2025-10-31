# Docker-Only Development Guide

## Overview

This project uses a **Docker-only development approach**. This means:
- ✅ No local Python installation required
- ✅ No virtual environments (venv) needed
- ✅ Consistent environment across all developers
- ✅ "Works on my machine" issues eliminated
- ✅ Production parity guaranteed

---

## Why Docker-Only?

### ❌ Problems with venv Approach

| Issue | Impact |
|-------|--------|
| **Inconsistency** | Different Python versions across machines |
| **"Works on my machine"** | Environment differences cause bugs |
| **Setup Complexity** | New developers need 15-20 minutes setup |
| **Dependency Conflicts** | pip, setuptools, system packages clash |
| **Production Mismatch** | Dev environment ≠ Production environment |
| **Multiple venvs** | 7 services = 7 venvs = ~3.5GB disk space |

### ✅ Benefits of Docker-Only

| Benefit | Value |
|---------|-------|
| **Perfect Consistency** | Identical environment for everyone |
| **Fast Onboarding** | New developers productive in 5 minutes |
| **No Dependencies** | Just Docker Desktop |
| **Production Parity** | Dev = Production |
| **Microservices Ready** | Built for distributed architecture |
| **Easy Cleanup** | `docker-compose down` removes everything |

---

## How It Works

### Traditional Development (What We DON'T Do)

```bash
# ❌ OLD WAY - Don't do this
cd appointment-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Problems:**
- Need Python 3.13 installed
- Need to activate venv every time
- Need to do this for each of 7 services
- Environment conflicts between services
- Hard to share exact setup with team

---

### Docker Development (What We DO)

```bash
# ✅ NEW WAY - Do this instead
docker-compose up -d
docker-compose exec appointment-service python manage.py migrate
```

**Benefits:**
- Everything in isolated containers
- One command starts all services
- Exact same environment for everyone
- No local Python needed

---

## Developer Workflow

### Daily Development

```bash
# Morning: Start everything
docker-compose up -d

# Work on code (files sync automatically)
# Edit code in VS Code, PyCharm, etc.
# Changes appear in container immediately

# Run commands when needed
docker-compose exec appointment-service python manage.py migrate
docker-compose exec appointment-service python manage.py test

# View logs
docker-compose logs -f appointment-service

# Evening: Stop everything
docker-compose down
```

### Installing New Packages

```bash
# 1. Edit requirements.txt
echo "new-package==1.0.0" >> appointment-service/requirements.txt

# 2. Rebuild container
docker-compose up -d --build appointment-service

# Done! Package installed in container
```

### Running Tests

```bash
# Run tests in container
docker-compose exec appointment-service python manage.py test

# With coverage
docker-compose exec appointment-service coverage run manage.py test
docker-compose exec appointment-service coverage report
```

### Debugging

```bash
# Option 1: Add print statements, check logs
docker-compose logs -f appointment-service

# Option 2: Interactive shell
docker-compose exec appointment-service python manage.py shell

# Option 3: Django debugger
# Add: import pdb; pdb.set_trace()
# Attach: docker attach appointment-service
```

---

## IDE Setup

### VS Code

**Option 1: Edit Locally, Run in Docker (Recommended)**

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "docker-compose exec appointment-service python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true
}
```

**Option 2: Remote Container Extension**

1. Install "Remote - Containers" extension
2. Click Docker icon in status bar
3. "Attach to Running Container"
4. Select appointment-service
5. Open folder: `/app`

---

### PyCharm Professional

1. **Settings** → **Project** → **Python Interpreter**
2. Click gear icon → **Add**
3. Select **Docker Compose**
4. Configuration file: `docker-compose.yml`
5. Service: `appointment-service`
6. Click OK

Now you can:
- Run/debug directly from PyCharm
- Use breakpoints
- View variables
- All running in Docker!

---

### PyCharm Community / Other IDEs

Edit code locally, run in Docker:

```bash
# In terminal
docker-compose up -d
docker-compose logs -f appointment-service
```

Files sync automatically via volume mounts.

---

## Common Tasks

### Create Django App

```bash
docker-compose exec appointment-service python manage.py startapp new_app
```

### Make Migrations

```bash
docker-compose exec appointment-service python manage.py makemigrations
docker-compose exec appointment-service python manage.py migrate
```

### Create Superuser

```bash
docker-compose exec authentication-service python manage.py createsuperuser
```

### Access Database

```bash
# PostgreSQL shell
docker-compose exec postgres psql -U postgres -d servease_appointments

# Django database shell
docker-compose exec appointment-service python manage.py dbshell
```

### Access Redis

```bash
docker-compose exec redis redis-cli
```

### Run Custom Management Command

```bash
docker-compose exec appointment-service python manage.py seed_timeslots --days=30
```

---

## File Structure

### ✅ What We Keep

```
appointment-service/
├── Dockerfile              ✅ Defines container
├── .dockerignore          ✅ What NOT to copy into image
├── requirements.txt        ✅ Python dependencies
├── manage.py              ✅ Django management
└── appointments/          ✅ Application code
```

### ❌ What We Avoid

```
appointment-service/
├── venv/                  ❌ Not needed (Docker isolates)
├── __pycache__/          ❌ Ignored by .gitignore
├── *.pyc                 ❌ Ignored by .dockerignore
└── .env                  ❌ In .gitignore (use .env.example)
```

---

## Troubleshooting

### "Module not found" Error

```bash
# Solution: Rebuild container
docker-compose up -d --build appointment-service
```

### "Port already in use"

```bash
# Find what's using port 8005
netstat -ano | findstr :8005  # Windows
lsof -i :8005                 # Mac/Linux

# Either kill that process or change port in docker-compose.yml
```

### "Database connection refused"

```bash
# Wait for postgres to be ready
docker-compose up -d
# Wait 10 seconds
docker-compose exec postgres pg_isready
```

### Code Changes Not Reflecting

```bash
# Check volume mounts in docker-compose.yml
# Should have: - ./appointment-service:/app

# Restart service
docker-compose restart appointment-service
```

### Container Keeps Crashing

```bash
# View detailed logs
docker-compose logs appointment-service

# Common causes:
# - Syntax error in Python code
# - Missing dependency in requirements.txt
# - Port conflict
# - Database not ready
```

---

## Team Collaboration

### Setting Up New Developer

1. **Install Docker Desktop** (5 minutes)
2. **Clone repository**
   ```bash
   git clone <repo>
   cd servease-backend
   ```
3. **Copy environment file**
   ```bash
   cp .env.example .env
   ```
4. **Start everything**
   ```bash
   docker-compose up -d
   ```
5. **Done!** Everything works identically to other developers.

### Sharing Environment Changes

When you update dependencies:

```bash
# 1. Update requirements.txt
echo "new-package==1.0.0" >> appointment-service/requirements.txt

# 2. Commit to git
git add appointment-service/requirements.txt
git commit -m "Add new-package for feature X"
git push

# 3. Team members update
git pull
docker-compose up -d --build appointment-service
```

Everyone gets the same package automatically!

---

## Performance Tips

### Speed Up Builds

**Use .dockerignore:**
```
# Exclude large, unnecessary files
venv/
__pycache__/
*.pyc
.git/
node_modules/
.pytest_cache/
```

**Layer Caching:**
```dockerfile
# Copy requirements first (changes less often)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code second (changes more often)
COPY . .
```

### Faster Restarts

```bash
# Restart without rebuilding
docker-compose restart appointment-service

# Only rebuild if requirements.txt changed
docker-compose up -d --build appointment-service
```

### Reduce Resource Usage

```yaml
# In docker-compose.yml, add limits:
appointment-service:
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
```

---

## Migration from venv to Docker

### If You Have Existing venv

1. **Delete it:**
   ```bash
   cd appointment-service
   rm -rf venv  # or rmdir /s venv on Windows
   ```

2. **Ensure requirements.txt is up to date:**
   ```bash
   # If you were using pip freeze
   pip freeze > requirements.txt
   ```

3. **Test in Docker:**
   ```bash
   docker-compose up -d --build appointment-service
   docker-compose logs appointment-service
   ```

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "Remove venv, use Docker-only development"
   ```

---

## Comparison Chart

| Task | venv Approach | Docker Approach |
|------|--------------|-----------------|
| **Install Python** | Download, install 3.13 | Not needed |
| **Create venv** | `python -m venv venv` | Not needed |
| **Activate venv** | Every terminal session | Not needed |
| **Install packages** | `pip install -r req.txt` | `docker-compose up -d --build` |
| **Run migrations** | `python manage.py migrate` | `docker-compose exec <service> python manage.py migrate` |
| **Start service** | `python manage.py runserver` | `docker-compose up -d` |
| **Disk space (7 services)** | ~3.5GB (7× venvs) | ~500MB (shared layers) |
| **Setup time** | 15-20 minutes | 5 minutes |
| **Consistency** | ⚠️ Variable | ✅ Perfect |
| **Production parity** | ⚠️ Approximate | ✅ Exact |
| **Cleanup** | Manual deletion | `docker-compose down -v` |

---

## Best Practices

### ✅ DO

- Use Docker for ALL development
- Keep Dockerfiles simple
- Use .dockerignore to exclude unnecessary files
- Document environment variables in .env.example
- Commit docker-compose.yml and Dockerfiles to git
- Use volume mounts for code (hot reload)
- Tag images with versions in production

### ❌ DON'T

- Don't create venv folders
- Don't commit .env files
- Don't put secrets in Dockerfiles
- Don't run `pip install` locally
- Don't edit code inside containers
- Don't use `latest` tag in production
- Don't ignore Docker logs

---

## FAQ

**Q: Do I need Python installed on my machine?**  
A: No! Docker containers include Python.

**Q: Can I still use pip?**  
A: Not directly. Add packages to `requirements.txt`, then rebuild container.

**Q: What about virtual environments?**  
A: Not needed. Docker provides better isolation than venv.

**Q: How do I update Python version?**  
A: Change `FROM python:3.13-slim` in Dockerfile, rebuild.

**Q: Can I use this on Windows/Mac/Linux?**  
A: Yes! Docker works identically on all platforms.

**Q: What if I want to use PyCharm debugger?**  
A: PyCharm Professional supports Docker remote interpreters with debugging.

**Q: Is this slower than local development?**  
A: Slightly slower container startup, but faster overall due to no venv management.

**Q: What about CI/CD?**  
A: Same Docker images used in development, testing, and production!

---

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Docker Best Practices](https://docs.docker.com/samples/django/)
- [VS Code Docker Extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
- [PyCharm Docker Integration](https://www.jetbrains.com/help/pycharm/docker.html)

---

**Summary:**  
Docker-only development provides consistency, simplicity, and production parity. No virtual environments needed—Docker handles all isolation and dependency management.

**Last Updated:** October 30, 2025  
**Status:** ✅ Recommended Approach

