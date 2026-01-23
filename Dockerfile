# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Fix for ChromaDB requiring newer sqlite3
RUN pip install pysqlite3-binary
ENV LD_LIBRARY_PATH=/usr/local/lib

# Install chromadb separately to isolate build failures
RUN pip install chromadb==0.4.24

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 8070 for FastAPI (and 8501 for Streamlit if running UI)
EXPOSE 8070 8501

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8070"]
