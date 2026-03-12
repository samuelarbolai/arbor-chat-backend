FROM python:3.11-slim
ENV PYTHONUNBUFFERED True

WORKDIR /app
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

# Cloud Run automatically provides the $PORT environment variable
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT