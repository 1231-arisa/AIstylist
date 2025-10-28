FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_hf.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/clothes/input output static/images

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=app_hf.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 7860

# Run the application
CMD ["python", "app_hf.py"]
