# FROM python:3.9-slim

# ENV PYTHONUNBUFFERED=1

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY supplement_expert /app/supplement_expert

# CMD ["streamlit", "run", "./supplement_expert/app.py"]

FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

RUN ls -l /app

# Copy the rest of the application
COPY . /app

# Make sure the entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Use an entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]