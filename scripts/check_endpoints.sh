#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-${BASE_URL:-http://localhost:8080}}"

echo "Checking health endpoint on ${BASE_URL}"
curl -sS "${BASE_URL}/" | sed 's/^/health: /'

echo "Checking summarize endpoint"
curl -sS -X POST "${BASE_URL}/summarize" \
  -H "Content-Type: application/json" \
  -d '{"input":"Artificial intelligence is transforming healthcare, finance, and logistics by improving predictions and automating complex tasks."}' \
  | sed 's/^/summarize: /'

echo "Checking structured summarize endpoint"
curl -sS -X POST "${BASE_URL}/summarize/structured" \
  -H "Content-Type: application/json" \
  -d '{"input":"Artificial intelligence is transforming healthcare, finance, and logistics by improving predictions and automating complex tasks."}' \
  | sed 's/^/structured: /'

echo "Done"
