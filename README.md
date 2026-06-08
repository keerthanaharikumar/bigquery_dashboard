# GA4 Analytics API — BigQuery + FastAPI + Dashboard

A REST API that queries the Google Analytics 4 public dataset from BigQuery and serves the results through 9 endpoints, with an interactive HTML dashboard. Containerized with Docker.

---

## Dashboard Preview

![Fast API Dashboard](/images/dashboard.jpeg)

---

## API Docs

![](/images/api.jpeg)

---
![](/images/docs.jpeg)


- Queries real GA4 e-commerce data from the `bigquery-public-data.ga4_obfuscated_sample_ecommerce` public dataset
- Exposes 9 REST API endpoints grouped by Events, Audience, and Ecommerce
- Serves an interactive dashboard that fetches live data from the API and visualizes it with charts and tables
- Fully containerized with Docker — runs anywhere with a valid GCP service account

---




---

## Tech Stack

- Python 3.11
- FastAPI
- Google BigQuery (google-cloud-bigquery)
- Pandas
- Docker + Docker Compose
- HTML + CSS + JavaScript (dashboard)

---



## Running with Docker

### Prerequisites
- Docker installed
- A GCP service account JSON key with the following roles:
  - BigQuery Data Viewer
  - BigQuery Job User
- A Google Cloud project with the BigQuery API enabled

### Steps

1. Clone the repository:
```bash
git clone https://github.com/your-username/pythonBigQ.git
cd pythonBigQ
```

2. Place your service account key in the project folder:
```bash
cp /path/to/your-key.json ./credentials.json
```

3. Set your project ID in `docker-compose.yml`:
```yaml
environment:
  - GCP_PROJECT_ID=your-project-id
```

4. Build and run:
```bash
docker compose up --build
```

5. Open in browser:
```
http://127.0.0.1:8000/docs       # API documentation
http://127.0.0.1:8000/static/dashboard.html  # Dashboard
```

---

## Running locally (without Docker)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gcloud auth application-default login
uvicorn main:app --reload
```

---

## Dataset

This project uses the [GA4 Obfuscated Sample Ecommerce dataset](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset) , a public BigQuery dataset provided by Google containing 12 months of real web analytics data from the Google Merchandise Store.

Available date range: `20201101` to `20211231`

-