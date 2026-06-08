FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000 
ENV GCP_PROJECT_ID=""
ENV GOOGLE_APPLICATION_CREDENTIALS=""
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
