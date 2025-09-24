# Use official Python slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy only requirements first (for caching)
COPY apps/backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY apps/backend/ .

# Expose FastAPI port
EXPOSE 8000

# Command to run FastAPI app
# Adjust import path if main.py is inside a folder like 'app'
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
