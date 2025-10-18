# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy Python requirements first for better caching
COPY requirements_hf.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_hf.txt

# Copy entire project
COPY . .

# Build React frontend
WORKDIR /app/lovable-project
RUN npm install
RUN npm run build

# Move back to app directory
WORKDIR /app

# Expose port 7860 (HF Spaces default)
EXPOSE 7860

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=7860

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the application
CMD ["python", "app_hf.py"]
