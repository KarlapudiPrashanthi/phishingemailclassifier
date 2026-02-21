FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/app/data

RUN mkdir -p /app/data

EXPOSE 5000 8501

CMD ["python", "main.py", "--api"]
