# AI-Powered Self-Healing Data Pipeline

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.10+%20%7C%203.0+-017CEE?logo=apache-airflow&logoColor=white)](https://airflow.apache.org/)
[![Ollama](https://img.shields.io/badge/Ollama-LLaMA%203.2-black?logo=ollama&logoColor=white)](https://ollama.ai/)
[![Docker](https://img.shields.io/badge/Docker-Compose%20Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-10%2F10%20Passing-brightgreen?logo=pytest&logoColor=white)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end, agentic data engineering pipeline designed to handle real-world dirty data. Using **Apache Airflow** and **Ollama (LLaMA 3.2)**, this pipeline automatically detects, diagnoses, and heals data quality anomalies on-the-fly during sentiment analysis, with graceful degradation and automated health monitoring.

Based on the tutorial: [Building Self-Healing Data Pipeline - End to End Data Engineering Project](https://www.youtube.com/watch?v=As1QSF3LnvA) by **CodeWithYu (Yusuf Ganiyu)**.

---

## 📑 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Self-Healing Capabilities](#self-healing-capabilities)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Option A: Docker Compose (Recommended)](#option-a-docker-compose-recommended)
  - [Option B: Local Python & Airflow](#option-b-local-python--airflow)
- [Ollama Setup & Models](#ollama-setup--models)
- [Running the Pipeline](#running-the-pipeline)
  - [1. Airflow UI Trigger](#1-airflow-ui-trigger)
  - [2. CLI Batch Runner](#2-cli-batch-runner)
- [Testing](#testing)
- [Health Monitoring & Outputs](#health-monitoring--outputs)
- [Configuration Reference](#configuration-reference)
- [Attribution](#attribution)

---

## 🔍 Overview

Traditional data pipelines break brittle workflows when encountering unexpected or corrupted data (missing values, wrong types, empty strings, emojis/special chars, or oversized payloads).

This project implements an **agentic, self-healing architecture**:
1. **Anomaly Diagnosis:** Real-time inspection of incoming records against data quality contracts.
2. **Automated Healing:** Dynamic remediation of defects (placeholder injection, type casting, text cleaning, smart truncation).
3. **Local LLM Inference:** Sentiment analysis classification and confidence scoring powered locally by Ollama (LLaMA 3.2).
4. **Graceful Degradation:** Automatic fallback to neutral sentiments and fallback tags if inference fails or times out.
5. **Observability & Health Checks:** Real-time generation of pipeline health grades (`HEALTHY`, `WARNING`, `DEGRADED`, `CRITICAL`) and analytics.

---

## 🏛️ Architecture

![Architecture](assets/Self%20healing%20pipeline.jpeg)

```
[ Input Data: JSONL Reviews ]
            │
            ▼
┌───────────────────────────────┐
│     Airflow Task: Load        │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│  Airflow Task: Diagnose & Heal│ ──> [ Detects 5 Data Quality Anomaly Types ]
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Airflow Task: Ollama Inference│ <── [ Ollama Local LLM: LLaMA 3.2 ]
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Airflow Task: Aggregate & Stats│ ──> [ JSON Summary & Anomaly Distribution ]
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Airflow Task: Health Report   │ ──> [ Pipeline Status: HEALTHY/WARNING/etc ]
└───────────────────────────────┘
```

---

## 🛡️ Self-Healing Capabilities

| Error Type | Anomaly Detection | Autonomous Healing Action |
|---|---|---|
| `missing_text` | Text field is `None` / null | Injects default fallback placeholder |
| `wrong_type` | Text field is non-string (e.g. integer, boolean, float) | Dynamic string type casting |
| `empty_text` | Text is empty string or only whitespace | Injects placeholder text |
| `special_characters_only` | Text contains zero alphanumeric characters (symbols/emojis only) | Replaces with `[Non-text content]` marker |
| `too_long` | Text exceeds threshold (default: 2,000 chars) | Smart character truncation with ellipsis (`...`) |

---

## 📁 Project Structure

```
self-healing-data-pipeline/
├── assets/
│   └── Self healing pipeline.jpeg     # Pipeline architecture diagram
├── dags/
│   └── agentic_pipeline_dag.py        # Airflow DAG with diagnosis, healing & LLM tasks
├── data/
│   └── sample_reviews.json            # Pre-generated sample dataset with clean & edge cases
├── scripts/
│   ├── batch_runner.py                # Multi-threaded CLI runner for Airflow DAG runs
│   └── generate_sample_data.py        # Synthetic review generator for edge case testing
├── tests/
│   └── test_healing.py                # Pytest & unittest suite covering all healing actions
├── docker-compose.yaml                # Multi-container orchestration (Airflow + Ollama + Postgres)
├── requirements.txt                   # Project dependencies
├── .gitignore                         # Ignore file excluding databases, logs, virtualenvs
└── README.md                          # Comprehensive documentation
```

---

## 🚀 Quick Start

### Option A: Docker Compose (Recommended)

Run the full stack (Airflow Webserver, Scheduler, Postgres DB, and Ollama) with a single command:

```bash
docker compose up -d
```

1. **Access Airflow UI:** Open [http://localhost:8080](http://localhost:8080)
   - **Username:** `admin`
   - **Password:** `admin`
2. **Pull LLaMA 3.2 into the Ollama container:**
   ```bash
   docker exec -it pipeline_ollama ollama pull llama3.2
   ```
3. Trigger the `self_healing_pipeline` DAG in the UI!

---

### Option B: Local Python & Airflow

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pavan2131/self-healing-data-pipeline.git
   cd self-healing-data-pipeline
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Airflow:**
   ```bash
   export AIRFLOW_HOME=$(pwd)
   # On Windows PowerShell:
   $env:AIRFLOW_HOME = (Get-Location).Path

   airflow db migrate
   airflow standalone
   ```

---

## 🦙 Ollama Setup & Models

Ensure [Ollama](https://ollama.ai) is installed and running:

```bash
# Start Ollama service
ollama serve

# Pull the lightweight, high-performance LLaMA 3.2 model
ollama pull llama3.2
```

To verify Ollama is responding:
```bash
ollama run llama3.2 "Classify the sentiment of: 'This software works smoothly!' as POSITIVE, NEGATIVE, or NEUTRAL."
```

---

## ⚡ Running the Pipeline

### 1. Airflow UI Trigger

Navigate to [http://localhost:8080](http://localhost:8080), unpause `self_healing_pipeline`, and trigger with custom configuration JSON:

```json
{
  "input_file": "data/sample_reviews.json",
  "batch_size": 25,
  "offset": 0,
  "ollama_model": "llama3.2"
}
```

### 2. CLI Batch Runner

Use `scripts/batch_runner.py` to trigger sequential or parallel DAG runs for large-scale datasets:

```bash
# Preview runs with dry-run mode
python scripts/batch_runner.py --total 1000 --batch-size 100 --dry-run

# Run sequentially in chunks of 50
python scripts/batch_runner.py --total 500 --batch-size 50

# Run concurrently with 4 workers
python scripts/batch_runner.py --total 5000 --batch-size 250 --parallel 4
```

### Generating Custom Test Datasets
```bash
python scripts/generate_sample_data.py --output data/sample_reviews.json --count 100
```

---

## 🧪 Testing

Run the included unit test suite to verify all diagnostic rules, healing transformations, and JSON parsing logic:

```bash
python -m unittest tests/test_healing.py
```
Or with `pytest`:
```bash
pytest tests/
```

All 10 tests validate:
- ✅ Clean reviews are unaltered
- ✅ Null review text healing
- ✅ Empty / whitespace string healing
- ✅ Numeric / boolean type conversion
- ✅ Special characters / emoji replacement
- ✅ Character length truncation
- ✅ Standard Ollama JSON parsing
- ✅ Markdown code-block wrapped JSON parsing
- ✅ Unstructured response fallback classification

---

## 📊 Health Monitoring & Outputs

Upon each run, the pipeline writes a detailed summary to `output/`:

```json
{
  "pipeline": "self_healing_pipeline",
  "health_status": "HEALTHY",
  "run_info": {
    "batch_size": 50,
    "offset": 0,
    "input_file": "data/sample_reviews.json"
  },
  "metrics": {
    "total_processed": 50,
    "success_rate": 0.58,
    "healing_rate": 0.42,
    "degradation_rate": 0.0
  },
  "sentiment_distribution": {
    "POSITIVE": 28,
    "NEGATIVE": 14,
    "NEUTRAL": 8
  },
  "healing_summary": {
    "filled_with_placeholder": 8,
    "type_conversion": 5,
    "replaced_special_characters": 4,
    "truncated_text": 4
  }
}
```

### Health Status Thresholds
- **`HEALTHY`**: Degradation rate = 0%, healed rate ≤ 50%
- **`WARNING`**: Healed rate > 50% of the batch
- **`DEGRADED`**: Degradation rate > 0% (one or more models failed or fell back)
- **`CRITICAL`**: Degradation rate > 10%

---

## ⚙️ Configuration Reference

| Environment Variable | Default | Description |
|---|---|---|
| `PIPELINE_BASE_DIR` | Project root | Base directory for file operations |
| `PIPELINE_INPUT_FILE` | `data/sample_reviews.json` | Path to JSONL review file |
| `PIPELINE_OUTPUT_DIR` | `output/` | Directory where summaries are stored |
| `PIPELINE_MAX_TEXT_LENGTH` | `2000` | Max character length before truncation |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.2` | Model name for inference |
| `OLLAMA_TIMEOUT` | `120` | Request timeout in seconds |
| `OLLAMA_RETRIES` | `3` | Retry attempts before falling back |

---

## 👏 Attribution & Credits

- Tutorial by **CodeWithYu (Yusuf Ganiyu)**: [Building Self-Healing Data Pipeline - End to End Data Engineering Project](https://www.youtube.com/watch?v=As1QSF3LnvA)
- Original Reference Repository: [airscholar/SelfHealingPipeline](https://github.com/airscholar/SelfHealingPipeline)
- Developed and maintained by [@pavan2131](https://github.com/pavan2131)
