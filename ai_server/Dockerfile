FROM python:3.10-slim

WORKDIR /app

COPY ai_server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ai_server /app/ai_server

CMD ["python", "-m", "ai_server.workers.job_worker"]
