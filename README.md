# ADK Text Summarizer (Cloud Run)

A minimal Google ADK agent deployed behind FastAPI on Cloud Run.

## What It Does

- Accepts text via `POST /summarize`
- Accepts structured summary requests via `POST /summarize/structured`
- Uses a Google ADK agent with Gemini (`gemini-2.0-flash` by default)
- Returns a concise summary as JSON
- Enforces structured summary contract: `title` + `bullets` (3-5 items)

## Project Files

- `agent.py`: ADK root agent and tool registration
- `main.py`: FastAPI app and ADK runner orchestration
- `requirements.txt`: Python dependencies
- `Dockerfile`: Container image build definition

## Local Run

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set API key:

```bash
# PowerShell
$env:GOOGLE_API_KEY="YOUR_API_KEY"
```

4. Start service:

```bash
python main.py
```

5. Test:

```bash
curl -X POST http://localhost:8080/summarize \
  -H "Content-Type: application/json" \
  -d '{"input":"Artificial intelligence is transforming healthcare, finance, and logistics by improving predictions, reducing manual work, and enabling new products."}'

curl -X POST http://localhost:8080/summarize/structured \
  -H "Content-Type: application/json" \
  -d '{"input":"Artificial intelligence is transforming healthcare, finance, and logistics by improving predictions, reducing manual work, and enabling new products."}'
```

## Deploy To Cloud Run

Create a secret once, then deploy using secret injection (recommended):

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
gcloud secrets create google-api-key --replication-policy=automatic
echo -n "YOUR_API_KEY" | gcloud secrets versions add google-api-key --data-file=-
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/adk-summarizer
gcloud run deploy adk-summarizer \
  --image gcr.io/YOUR_PROJECT_ID/adk-summarizer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_MODEL=gemini-2.0-flash \
  --set-secrets GOOGLE_API_KEY=google-api-key:latest
```

Grant runtime access to the secret for your Cloud Run service account:

```bash
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gcloud secrets add-iam-policy-binding google-api-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

Get URL:

```bash
gcloud run services describe adk-summarizer --region us-central1 --format 'value(status.url)'
```

## IAM And Security Notes

- For evaluation/public testing, `--allow-unauthenticated` is simplest.
- For restricted access, remove that flag and grant invoker role:

```bash
gcloud run services add-iam-policy-binding adk-summarizer \
  --region us-central1 \
  --member=user:you@example.com \
  --role=roles/run.invoker
```

- This project uses Secret Manager-first deployment for `GOOGLE_API_KEY`.

## Smoke Tests

Run lightweight endpoint tests:

```bash
pytest -q
```

## Quick Curl Script

Use the helper script for local or deployed endpoint checks:

```bash
# Local default (http://localhost:8080)
bash scripts/check_endpoints.sh

# Cloud Run URL
bash scripts/check_endpoints.sh https://YOUR-CLOUD-RUN-URL
```

## CI

GitHub Actions workflow runs `pytest -q` on every push:

- `.github/workflows/ci.yml`
