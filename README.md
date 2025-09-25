# ServEase Backend (Microservices)

This repository contains the backend implementation of the **ServEase** platform using **Django** with a **microservice architecture**.  
Each service runs independently and communicates via APIs.

---

## 🚀 Microservices in this Repo

- **Authentication Service**
- **Customer Service**
- **Employee Service**
- **Vehicle & Project Service**
- **Appointment Service**
- **Notification Service**
- **Chatbot Service**

---

## 📦 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/ServEase-EAD/servease-backend.git
cd servease-backend
```

### 2. Create & activate virtual environment

We use Pipenv for dependency management.

```bash
pipenv install django
pipenv shell
```

### 3. Running a service

Navigate into the desired service folder and start the server on a unique port:

```bash
cd <service-folder>
python manage.py runserver <port>
```

Example ports you can use for each service:

- Authentication Service → 8001
- Customer Service → 8002
- Employee Service → 8003
- Vehicle & Project Service → 8004
- Appointment Service → 8005
- Notification Service → 8006
- Chatbot Service → 8007

---

## 📝 Development Notes

- Each service maintains its own database (`db.sqlite3` by default).
- You can configure PostgreSQL/MySQL in `settings.py` for production.
- Ensure each service runs on a different port to avoid conflicts.
- Use API calls between services to communicate.

---

## 🤝 Contributing

1. Fork the repo
2. Create a new branch (`feature/my-feature`)
3. Commit changes
4. Push and open a Pull Request

---