FROM python:3.11-slim

# Install Java (OpenJDK 17) and other system dependencies
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless procps curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure the JDBC driver is present (re-download to be safe/consistent in docker build)
RUN python download_jdbc.py

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
