# Explainable Mental Health Risk Detection System

An end-to-end Explainable AI (XAI) mental health risk detection system using pre-trained Transformer models (BERT & RoBERTa) and traditional ML baselines (Logistic Regression & SVM with TF-IDF). The project features a Streamlit-based web dashboard to input user posts, predict suicide risk vs. non-risk behavior, and render attribution explanations with SHAP.

---

## Directory Structure

```text
project-3/
├── data/                        # Dataset directory (place Suicide_Detection.csv here)
│   └── processed/               # Stratified train/val/test splits + EDA plots
├── models/                      # Saved model artifacts (.pkl, transformer checkpoints)
├── ai_model/src/
│   ├── baseline_models.py       # TF-IDF + Logistic Regression / SVM training & inference
│   ├── transformer_models.py    # BERT & RoBERTa fine-tuning and inference
│   └── multi_tier_classifier.py # Rule-based risk-tier escalation on top of binary probability
├── backend/src/
│   ├── main.py                  # FastAPI app entrypoint
│   ├── config/settings.py       # Shared path and parameter configuration
│   ├── api/routes.py            # REST endpoints (/analyze, /what-if, /search, /fairness, ...)
│   ├── services/                # Explainability, anonymizer, emotion analysis, fairness
│   │                             # auditing, robustness testing, clinical response drafting,
│   │                             # semantic case search, report generation
│   └── utils/preprocessing.py   # Text cleaning + stratified dataset splitting
├── frontend/                    # React (Vite) single-page app — Sandbox, What-If, Cases,
│   └── src/                     # Fairness, Analytics/Robustness, and Temporal Trend tabs
├── tests/                       # Pytest suite for preprocessing, services, and the pipeline
├── requirements.txt             # Python dependencies (backend + ML)
└── README.md                    # Main documentation
```

---

## Installation & Setup

1. **Clone or navigate** to the project directory:
   ```bash
   cd E:/Freelancing/project-3
   ```

2. **Create and activate a Python virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Add the dataset**:
   Download the [Suicide Watch Dataset from Kaggle](https://www.kaggle.com/datasets/nikhileshwarakomati/suicide-watch) and place the `Suicide_Detection.csv` file at `data/Suicide_Detection.csv`. `preprocessing.py` requires this file to be present and will raise an error if it's missing — there is no synthetic fallback.

6. **(Optional) Configure the Gemini-backed clinical narrative**:
   Copy `.env.example` to `.env` and set `GOOGLE_API_KEY` to a [Google AI Studio](https://aistudio.google.com/apikey) key. This powers the AI-generated clinical rationale in the RAG copilot's "DSM-5 RAG Grounding" tab. `.env` is gitignored — never commit it. Without a key, that feature falls back to a deterministic template automatically; nothing else in the app requires it.

---

## Usage Workflow

### 1. Data Ingestion & Preprocessing
Clean text, generate exploratory plots, and create stratified train/validation/test splits:
```bash
python backend/src/utils/preprocessing.py
```

### 2. Train Baselines
Train the TF-IDF vectorizer, Logistic Regression, and calibrated SVM:
```bash
python ai_model/src/baseline_models.py
```

### 3. Fine-Tune Transformers
Fine-tune BERT and RoBERTa (uses CUDA if available, otherwise falls back to CPU):
```bash
python ai_model/src/transformer_models.py --model bert     # Options: bert, roberta
python ai_model/src/transformer_models.py --model roberta --quick  # --quick for a fast smoke test
```

### 4. Run the Backend API
```bash
cd backend/src
uvicorn main:app --reload --port 8000
```

### 5. Run the Frontend
In a separate terminal:
```bash
cd frontend
npm run dev
```
Then open the printed local URL (default `http://localhost:5173`) in a browser. The frontend talks to the backend at `http://localhost:8000/api`.

### 6. Run Tests
```bash
pytest tests/ -v
```
