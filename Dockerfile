FROM python:3.11-slim
ENV PYTHONUNBUFFERED True

WORKDIR /app
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

# Cloud Run automatically provides the $PORT environment variable
CMD uvicorn main:app --host 0.0.0.0 --port $PORT

# gcloud run deploy arbor-chat-backend \
#   --source . \
#   --region us-central1 \
#   --allow-unauthenticated \
#   --project arbor-2026