FROM python:3.11-slim

RUN apt-get update && \
    apt-get install --no-install-recommends -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# make sure the log files exist
RUN mkdir -p logs && \
    touch logs/requests.txt logs/dbcount.txt

EXPOSE 8000

# create SQLite file and tables on startup
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
