# X-MHRDS — Explainable Mental Health Risk Detection System

> **MSc Advanced Artificial Intelligence Projects in Data Science — Module 55-710603**
> Sheffield Hallam University — Group Project

**X-MHRDS** is a research prototype that classifies social media posts for suicide risk language and wraps every prediction in a full explainability, fairness, robustness, calibration, and clinical decision-support stack. It is explicitly **not a clinical instrument**. Every component exists to answer a trust question about the classifier, not just to improve raw accuracy.

---

## Team

| Name | Student ID | Role |
|---|---|---|
| Shirisha Srirangam | C5057017 | Data pipeline, TF-IDF vectorizer, Logistic Regression, SVM, temperature scaling calibration |
| Vara Prasad Kurella | C5067650 | BERT and RoBERTa fine-tuning, gradient clipping, EMA weights |
| Sai Krishna Samudrapu | C4060587 | SHAP, Integrated Gradients, LIME, LOO, Multi-XAI convergence, four-tier risk escalation |
| John Babu Thammisetti | C5050552 | Fairness audit, construct validity, robustness testing, drift detection, OOD |
| Raviteja Vibhuthi | C5060678 | FastAPI backend, React dashboard, clinical copilot, Gemini RAG, live monitor |

---

## What the System Does

Four models are trained side by side to benchmark the interpretability-accuracy trade-off:

| Model | Representation | Test Accuracy | Test F1 |
|---|---|---|---|
| Logistic Regression | TF-IDF (uni+bigram, 5,000 features) | 91.38% | 91.20% |
| SVM (Calibrated LinearSVC) | TF-IDF (uni+bigram, 5,000 features) | 91.91% | 91.84% |
| BERT (bert-base-uncased, fine-tuned) | WordPiece, 128-token context | 97.69% | 97.68% |
| RoBERTa (roberta-base, fine-tuned) | Byte-pair encoding, 128-token context | 97.64% | 97.65% |

Every prediction is wrapped in:
- Four independent explanation methods (SHAP, Integrated Gradients, LIME, Leave-One-Out) with pairwise Pearson convergence analysis
- A four-tier clinical risk escalation engine (No Risk, Mild Distress, Moderate Risk, Severe Active Risk)
- A linguistic register fairness audit across Youth Slang, Formal Language, and Literal/Direct phrasing
- A construct validity audit confirming models detect crisis-specific language, not generic negativity
- Robustness stress testing under typo injection and distracting text
- Population Stability Index drift monitoring
- Energy-based out-of-distribution detection and Monte Carlo Dropout predictive uncertainty
- A live real-time monitoring feed with trend and change-point detection
- A Gemini-backed retrieval-augmented generation clinical copilot
- A full clinical decision-support layer with emotion tagging, cognitive distortion analysis, and draft response generation

---

## Directory Structure

```
X-MHRDS/
├── .env.example                  # Template for GOOGLE_API_KEY (copy to .env, never commit .env)
├── requirements.txt              # All Python dependencies
├── run.bat                       # One-command launcher for Windows
├── run.sh                        # One-command launcher for macOS/Linux
├── README.md                     # This file
├── PROJECT_PLAYBOOK.md           # Full technical documentation and Q&A guide
├── DEMO_GUIDE.md                 # Live demo click-by-click script
│
├── literature_review/
│   ├── literature_review.md      # Structured review of 16 papers (2026 arXiv)
│   ├── literature_review.docx    # Word export of the literature review
│   └── papers/                   # 14 source PDFs (2 paywalled, represented as placeholders)
│
├── ai_model/src/
│   ├── baseline_models.py        # TF-IDF vectorizer + Logistic Regression + calibrated SVM
│   ├── transformer_models.py     # BERT and RoBERTa fine-tuning with EMA, OOD, MC-Dropout
│   ├── multi_tier_classifier.py  # Four-tier risk escalation (ML path + threshold fallback)
│   └── calibration.py            # Temperature scaling + Expected Calibration Error
│
├── backend/src/
│   ├── main.py                   # FastAPI app, CORS, structured logging, exception handler
│   ├── db.py                     # SQLite schema and queries
│   ├── logging_config.py         # Shared logger factory
│   ├── config/
│   │   └── settings.py           # All tunable constants in one place
│   ├── api/
│   │   ├── routes.py             # Mounts the v1 router
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/        # health, sandbox, cases, analytics, temporal, monitor, copilot
│   ├── schemas/                  # Pydantic request and response models
│   ├── services/                 # All business logic — 20 modules
│   │   ├── explainability.py     # SHAP, Integrated Gradients, LIME, Leave-One-Out, What-If
│   │   ├── fairness_auditor.py   # Linguistic register fairness audit with bootstrapped CIs
│   │   ├── fairness_cohort_data.py # 96 hand-authored fairness scenarios
│   │   ├── construct_validity_auditor.py # Dehghan and Ashrafi (2026) residualization protocol
│   │   ├── robustness.py         # Typo injection and distracting text perturbation testing
│   │   ├── drift_detector.py     # Population Stability Index drift monitoring
│   │   ├── anonymizer.py         # Regex PII masking (five categories)
│   │   ├── emotion_analyzer.py   # Six-category lexical emotion detection
│   │   ├── cognitive_distortion_analyzer.py # Ten Beck/Burns CBT distortion categories
│   │   ├── clinical_helper.py    # Tier-specific draft response templates
│   │   ├── semantic_search.py    # TF-IDF cosine case retrieval
│   │   ├── report_generator.py   # HTML clinical report generator
│   │   ├── clinical_copilot.py   # SHA-256 compliance hash and simulated dispatch
│   │   ├── rag_copilot.py        # DSM-5 and C-SSRS keyword retrieval plus Gemini narrative
│   │   ├── gemini_client.py      # Google Generative AI SDK wrapper
│   │   ├── translation.py        # Multilingual detection, translation, attribution projection
│   │   ├── monitor_manager.py    # Live monitor background task
│   │   ├── feed_simulator.py     # Five synthetic user storylines
│   │   └── trend_analyzer.py     # OLS trend slope and Binary Segmentation change-point detection
│   └── utils/
│       └── preprocessing.py      # Text cleaning, PII masking, stratified dataset splitting
│
├── data/
│   ├── Suicide_Detection.csv     # Raw Kaggle dataset — NOT committed, download separately
│   ├── app.db                    # SQLite runtime database (auto-created on first run)
│   └── processed/                # train.csv, val.csv, test.csv, and two EDA plots
│
├── models/                       # All trained artifacts — NOT committed (too large)
│   ├── logistic_regression.pkl
│   ├── svm_classifier.pkl
│   ├── tfidf_vectorizer.pkl
│   ├── bert_model/               # BERT checkpoint directory
│   ├── roberta-base/             # RoBERTa checkpoint directory
│   └── *_calibration.pkl, *_ood.pkl, *_metrics.pkl files per model
│
├── frontend/
│   ├── index.html
│   ├── main.jsx
│   ├── App.jsx
│   ├── App.css
│   └── src/
│       ├── components/
│       │   ├── layout/           # Sidebar, Header, CommandPalette
│       │   ├── sandbox/          # SandboxTab, WordImportance, MultiXAIComparisonStudio
│       │   ├── analytics/        # AnalyticsTab, DriftDashboard
│       │   ├── copilot/          # ClinicalCopilotModal
│       │   ├── cases/            # Historical retrieval tab
│       │   ├── fairness/         # Demographic audit tab
│       │   ├── temporal/         # Temporal trajectory tab
│       │   ├── whatif/           # What-If perturbation tab
│       │   ├── monitor/          # Live stream monitor tab
│       │   └── landing/          # LandingPage (static, shown before dashboard)
│       ├── context/              # Theme, App, Analysis, Monitor, Notification providers
│       ├── hooks/                # One-line useX() wrapper per context
│       └── services/
│           └── apiClient.js      # Fetch-based API client
│
└── tests/
    ├── test_advanced_features.py  # Anonymizer, multi-tier, emotion, clinical helper, what-if
    ├── test_api_routes.py         # Full FastAPI route coverage across all four models
    ├── test_drift_detector.py     # PSI calculation and drift-metrics response shape
    ├── test_monitor_and_db.py     # DB, monitor lifecycle, WebSocket, trend and change-point
    ├── test_pipeline.py           # Text cleaning, config paths, robustness perturbations
    ├── test_rag_copilot.py        # RAG retrieval, C-SSRS protocol, Gemini fallback paths
    ├── test_translation_pipeline.py # Language detection, translation, token alignment
    └── test_xai_comparison.py     # Pearson correlation helper
```

---

## Environment Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/X-MHRDS.git
cd X-MHRDS
```

### Step 2 — Create and Activate a Python Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS and Linux
source venv/bin/activate
```

### Step 3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### Step 5 — Download the Dataset

Download the **Suicide Watch Dataset** from Kaggle:
https://www.kaggle.com/datasets/nikhileshwarakomati/suicide-watch

Place the file at exactly this path:
```
data/Suicide_Detection.csv
```

The preprocessing script raises a `FileNotFoundError` if this file is missing. There is no synthetic fallback. This is intentional.

### Step 6 — Configure Gemini (Optional)

The Gemini-backed clinical narrative in the RAG copilot is entirely optional. Everything else in the system works without it.

If you want to enable it:
```bash
cp .env.example .env
```

Then open `.env` and set your Google AI Studio API key:
```
GOOGLE_API_KEY=your_key_here
```

Get a free key at: https://aistudio.google.com/apikey

The `.env` file is gitignored. Never commit it. Without a key, the RAG copilot falls back to a deterministic template automatically with no error.

---

## Training the Models

Run these commands in order. Each script is independently runnable and idempotent.

### Step 1 — Preprocess the Dataset

```bash
python backend/src/utils/preprocessing.py
```

This cleans text, masks PII, generates stratified train/val/test splits (70/15/15), and produces two EDA plots. Output goes to `data/processed/`.

### Step 2 — Train the Baseline Models

```bash
python ai_model/src/baseline_models.py
```

This fits the shared TF-IDF vectorizer, trains Logistic Regression and calibrated SVM, evaluates on the test split, and fits temperature scaling calibration on the validation split.

### Step 3 — Fine-Tune the Transformer Models

```bash
# Fine-tune BERT
python ai_model/src/transformer_models.py --model bert

# Fine-tune RoBERTa
python ai_model/src/transformer_models.py --model roberta
```

Add `--quick` for a fast smoke test (1 epoch, 100 train rows):
```bash
python ai_model/src/transformer_models.py --model bert --quick
```

CUDA is used automatically if available. Falls back to CPU if not. Each full training run takes approximately 20 to 40 minutes on GPU and significantly longer on CPU.

### Step 4 — Optional Audits (run from backend/src)

```bash
cd backend/src

# Robustness stress testing
python -m services.robustness

# Construct validity audit
python -m services.construct_validity_auditor

cd ../..

# Multi-tier classifier ML path (fallback threshold rules are used by default without this)
python ai_model/src/multi_tier_classifier.py
```

---

## Running the Application

### Option A — One Command (Recommended)

From the project root:

```bash
# Windows
run.bat

# macOS and Linux
bash run.sh
```

This creates the virtual environment and node_modules if missing, then starts both servers.

### Option B — Manual Start

**Terminal 1 — Backend:**
```bash
cd backend/src
uvicorn main:app --reload --port 8000
```

Verify the backend is running by opening:
```
http://localhost:8000/
```

You should see: `{"status": "online", ...}`

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Then open:
```
http://localhost:5173
```

---

## Running the Test Suite

```bash
pytest tests/ -v
```

**8 test files, 70 passing test functions.** Wall clock approximately 134 seconds, dominated by model loading.

No frontend test suite exists. Frontend verification is manual only.

---

## Pre-Trained Models

The trained model artifacts are too large to commit to GitHub. You have two options:

**Option 1 — Train from scratch** following the training steps above.

**Option 2 — Download pre-trained artifacts** (if shared by the team):

Place all downloaded files under `models/` following the directory structure above. The application will load them automatically on first request via `lru_cache` singletons.

Model artifacts required for full functionality:
- `models/tfidf_vectorizer.pkl`
- `models/logistic_regression.pkl`
- `models/svm_classifier.pkl`
- `models/bert_model/` (full Hugging Face checkpoint directory)
- `models/roberta-base/` (full Hugging Face checkpoint directory)
- Per-model calibration, OOD threshold, and metrics `.pkl` files

---

## Quick Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Every tab shows "Failed to fetch" | Backend is not running | Run `uvicorn main:app --reload --port 8000` from `backend/src` |
| "No trained model metrics found" | Model pkl file missing from `models/` | Train the model or switch to a trained model in the selector |
| Drift and Fairness tabs show flat defaults | Database is empty | Run two or three Sandbox analyses first, then refresh |
| RAG narrative shows "Template" not "AI-generated" | No GOOGLE_API_KEY in .env | Add a valid key to `.env` or demo with the template fallback |
| SHAP takes a long time | Expected on CPU, SHAP is the slowest method | Narrate while it runs, do not click again |
| Live Monitor stays empty after Start | WebSocket tick takes up to 6 seconds | Wait one full tick before assuming an error |

---

## Known Limitations

These are stated proactively because knowing what the system cannot do is as important as knowing what it can.

1. The four-tier risk labels are heuristically synthesised from keyword rules, not human-annotated clinical labels
2. The fairness cohort has only 16 true-risk examples per linguistic register, below the audit's own 30-example statistical certification threshold
3. The Temporal Trajectory tab scores a fixed hardcoded 4-post demo timeline, not real per-user logged history
4. Historical case search is TF-IDF cosine similarity, not embedding-based semantic search
5. Multilingual translation is a small hardcoded dictionary plus an optional third-party fallback, not a trained translation model
6. All Clinical Copilot dispatch actions are explicitly simulated with no real external system integration
7. OOD detection and MC-Dropout uncertainty are available for BERT and RoBERTa only, not the TF-IDF baselines
8. Three frontend components are fully implemented but not currently rendered: TrustSignals, CognitiveDistortions, and AnonymizerDiff
9. No authentication, authorisation, or rate limiting on any API endpoint
10. PII anonymisation is regex-based, not a trained named entity recognition model

---

## API Reference

All endpoints are prefixed with `/api`. The backend must be running on port 8000.

| Method | Endpoint | Description |
|---|---|---|
| GET | /status | Liveness check |
| POST | /analyze | Full single-post analysis pipeline |
| POST | /what-if | Counterfactual word-swap re-analysis |
| POST | /explain-comparison | Four-explainer Multi-XAI comparison with correlation matrix |
| POST | /multilingual-analyze | Translate, analyse, and back-project attributions |
| GET | /cases | List seeded historical cases |
| POST | /search | TF-IDF similarity search over cases |
| POST | /report | Generate HTML clinical report |
| GET | /fairness | Linguistic register fairness audit |
| GET | /construct-audit | Construct validity (negativity confound) audit |
| GET | /metrics | Test-set accuracy, precision, recall, F1 per model |
| GET | /robustness | Typo and distraction robustness metrics per model |
| GET | /drift-metrics | PSI, histogram, and emotion shift between baseline and live stream |
| GET | /temporal | Fixed four-post demo timeline scored by selected model |
| POST | /monitor/start | Start the simulated live feed |
| POST | /monitor/stop | Stop the simulated live feed |
| GET | /monitor/users | Per-user trend and change-point snapshot |
| WS | /ws/monitor | Live WebSocket event stream |
| POST | /copilot/rag-query | DSM-5 and C-SSRS retrieval plus Gemini or template narrative |
| POST | /copilot/audit | HIPAA-style compliance audit and triage bundle |
| POST | /copilot/dispatch-protocol | Simulated safety-protocol dispatch |

---

## Technology Stack

**Backend:** Python 3.10, FastAPI, uvicorn, PyTorch, Hugging Face Transformers, scikit-learn, SHAP, ruptures, SQLite

**Frontend:** React 19, Vite 8, lucide-react

**AI Models:** bert-base-uncased, roberta-base (both fine-tuned), TF-IDF with Logistic Regression and calibrated LinearSVC

**Optional:** Google Generative AI SDK (Gemini) for RAG narrative

---

## Academic Integrity

This project was developed as part of MSc coursework at Sheffield Hallam University. All code, models, and documentation represent the original work of the team members listed above.

AI tools were used at AITS Level 2 (AI for Shaping) to assist with structuring documentation and improving written expression. All technical implementation, experimental results, and critical analysis are human-generated.

**This system is a research prototype. It is not a clinical instrument. No diagnosis should ever be made based on its output. A trained professional must always be involved in any real-world response to a crisis.**

---

## License

This repository is submitted as academic coursework. All rights reserved by the authors. Not licensed for commercial use or clinical deployment.
