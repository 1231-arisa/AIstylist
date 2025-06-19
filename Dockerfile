# Use official Python runtime as the base image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies required for certain Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 7860

# Command to run the application
CMD ["gunicorn", "--workers", "1", "--timeout", "600", "--bind", "0.0.0.0:7860", "run:app"]
