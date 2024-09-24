FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY supplement_expert /app/supplement_expert

CMD ["streamlit", "run", "./supplement_expert/app.py"]