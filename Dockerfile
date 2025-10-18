# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal for faster build)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements first for better caching
COPY requirements_minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Copy Python files and necessary assets
COPY app_hf.py .
COPY rag_pipeline.py .
COPY preprocess.py .

# Copy model files (these may be in LFS)
COPY faiss_index.bin .
COPY sentences.pkl .

# Copy images
COPY bot_avatar.png ./
COPY NMIMS_LOGO.png ./

# Copy pre-built React frontend
COPY static_build ./static

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
