FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements_full.txt ./requirements_full.txt
RUN pip install --no-cache-dir -r requirements_full.txt

# Copy application code
COPY backend ./backend
COPY agent ./agent
COPY classifier ./classifier
COPY crawler ./crawler
COPY evaluation ./evaluation
COPY relevance_model ./relevance_model
COPY data ./data
COPY README.md ./README.md
COPY QUICK_START.md ./QUICK_START.md
COPY IMPLEMENTATION_SUMMARY.md ./IMPLEMENTATION_SUMMARY.md

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
