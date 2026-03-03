FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create backend package structure and copy app
COPY app backend/app

# Create __init__.py files for package structure
RUN touch backend/__init__.py backend/app/__init__.py backend/app/routers/__init__.py backend/app/services/__init__.py

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

