# FastAPI PostgreSQL Docker Project

## 📌 Introduction

This project uses **FastAPI** as the backend, **PostgreSQL** as the database, and **Docker** to manage the development environment. The system supports RESTful APIs with JWT authentication, CRUD for entities, and integrated API documentation.

## 🛠 Technologies Used

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **API Documentation**: OpenAPI (Swagger UI)

## 📂 Project Structure

```
/project-root
│── alembic/                # Database migrations
│   ├── versions/           # Migration scripts
│── app/
│   ├── main.py             # Main entry point of the FastAPI application
│   ├── api/                # API routes
│   │   ├── v1/             # API versioning
│   │   │   ├── endpoints/  # Endpoint definitions
│   ├── core/               # Core settings and configurations
│   ├── models/             # Database model definitions
│   ├── repositories/       # Data access layer (CRUD operations)
│   ├── schemas/            # Pydantic schemas for data validation
│   ├── services/           # Business logic handlers
│   ├── utils/              # Utility functions
│── .env                    # Environment variables
│── Dockerfile              # Docker configuration
│── docker-compose.yml      # Docker Compose configuration
│── requirements.txt        # Required dependencies
│── README.md               # Usage instructions
```


## 🚀 Installation & Running the Application

### 1️⃣ Clone the Project

```sh
git clone https://github.com/mthuwhihand/basic-api-with-fastapi.git
cd basic-api-with-fastapi
```

### 2️⃣ Create a `.env` File

Create a `.env` file in the root directory and configure the environment variables:

```env
APP_NAME=<your_app_name>

#Admin account
ADMIN_NAME=Admin
ADMIN_EMAIL=admin@gmail.com
ADMIN_PASSWORD=admin

#For DB Container on Docker
DATABASE_PORT=5432
POSTGRES_PASSWORD=password
POSTGRES_USER=postgres
POSTGRES_DB=w1_db
POSTGRES_HOST=postgres_db
POSTGRES_HOSTNAME=127.0.0.1

#JWT
ACCESS_TOKEN_EXPIRES_IN=5
REFRESH_TOKEN_EXPIRES_IN=30
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=<your_secret_key>

```

### 3️⃣ Run with Docker Compose

```sh
docker compose up -d
```

### 4️⃣ Access the API

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

📌 **Contact:** If you have any questions, please reach out via email or open an issue on GitHub.
