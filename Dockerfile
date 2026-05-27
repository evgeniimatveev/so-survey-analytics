FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY dashboard/ ./dashboard/

RUN mkdir -p data

EXPOSE 7860

CMD ["bash", "dashboard/start.sh"]
