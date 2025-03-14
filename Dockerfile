FROM python:3.13.2-alpine3.21

# Set up working folder in container
WORKDIR /app

# Copy significant folder into container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && pip install alembic

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

