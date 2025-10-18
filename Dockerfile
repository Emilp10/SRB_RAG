# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy Python requirements first for better caching
COPY requirements_hf.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_hf.txt

# Copy Python files and necessary assets
COPY app_hf.py .
COPY rag_pipeline.py .
COPY preprocess.py .
COPY faiss_index.bin .
COPY sentences.pkl .
COPY SRB-2025.pdf .
COPY *.png ./

# Copy and build React frontend
COPY lovable-project ./lovable-project
WORKDIR /app/lovable-project
RUN npm ci --only=production
RUN npm run build

# Move built frontend to static directory
WORKDIR /app
RUN mkdir -p static && cp -r lovable-project/dist/* static/

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
