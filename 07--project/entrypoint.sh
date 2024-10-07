#!/bin/bash
set -e

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
until curl -s http://ollama:11434/ | grep -q "Ollama is running"; do
    sleep 5
done
echo "Ollama is ready!"

# Pull the Phi-3 model
echo "Pulling Phi3 model..."
curl -X POST http://ollama:11434/api/pull -d '{"name": "phi3"}'
echo "Phi3 model pulled successfully!"

# Wait for Phi-3 model to be available
echo "Waiting for Phi3 model to be ready..."
max_attempts=24
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://ollama:11434/api/tags | grep -q "phi3"; then
        echo "Phi3 model is present!"
        break
    fi
    attempt=$((attempt+1))
    echo "Attempt $attempt: Phi3 model not ready yet. Waiting..."
    sleep 20
done

if [ $attempt -eq $max_attempts ]; then
    echo "Error: Phi3 model failed to become ready after multiple attempts."
    exit 1
fi

# Wait for Elasticsearch to be ready
echo "Waiting for Elasticsearch to be ready..."
until curl -s http://elasticsearch:9200 >/dev/null; do
    sleep 1
done
echo "Elasticsearch is ready!"

# Wait for Postgres to be ready
echo "Waiting for Postgres to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
    sleep 1
done
echo "Postgres is ready!"

# Start Streamlit app
exec streamlit run ./supplement_expert/app.py