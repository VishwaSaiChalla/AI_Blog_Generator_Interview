# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        curl \
        wget \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p generated_posts reviews \
    && chmod 755 generated_posts reviews

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check for the Flask application
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Alternative health check using wget if curl fails
# HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
#     CMD wget --quiet --tries=1 --spider http://localhost:5000/ || exit 1

# Run the application
CMD ["python", "app.py"]
