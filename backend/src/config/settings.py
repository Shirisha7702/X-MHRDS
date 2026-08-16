import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Subdirectories creation
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Dataset settings
RAW_DATA_PATH = os.path.join(DATA_DIR, "Suicide_Detection.csv")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Persistence settings
DB_PATH = os.path.join(DATA_DIR, "app.db")

# Data Split Paths
TRAIN_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "train.csv")
VAL_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "val.csv")
TEST_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "test.csv")

# Prototyping Settings
# Subsample size for rapid development. Set to None to use the full dataset (232k+ records)
SAMPLE_SIZE = 15000 
RANDOM_STATE = 42
TEST_SPLIT = 0.15
VAL_SPLIT = 0.15

# Baseline Model settings
TFIDF_MAX_FEATURES = 5000
LR_MAX_ITER = 1000
SVM_C = 1.0

# Transformer Model settings
BERT_MODEL_NAME = "bert-base-uncased"
ROBERTA_MODEL_NAME = "roberta-base"
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 3
LEARNING_RATE = 2e-5

# Training stability settings
WARMUP_RATIO = 0.1
EMA_DECAY = 0.999
USE_MIXED_PRECISION = True

# Out-of-distribution (energy-based, Liu et al. 2020) and predictive-uncertainty
# (MC-Dropout) settings. Both are transformer-only: the energy score needs raw
# pre-softmax logits, and MC-Dropout needs dropout layers, neither of which the TF-IDF
# baselines have an architecturally faithful equivalent of.
OOD_ENERGY_TEMPERATURE = 1.0
OOD_PERCENTILE_THRESHOLD = 95
MC_DROPOUT_PASSES = 20

# Explainability settings
SHAP_MAX_EVALS = 500
LIME_NUM_FEATURES = 10
LIME_NUM_SAMPLES = 100

# Fairness audit settings
FAIRNESS_MIN_SUBGROUP_SIZE = 30
FAIRNESS_BOOTSTRAP_ITERATIONS = 1000

# Escalation trend detection settings (Live Monitor)
TREND_ESCALATING_SLOPE_THRESHOLD = 0.05
TREND_DEESCALATING_SLOPE_THRESHOLD = -0.05
TREND_HISTORY_LIMIT = 20

# Change-point detection settings (ruptures): a candidate change point is only reported
# once there is enough history to fit a break, and only if the mean shift it produces
# clears a minimum magnitude -- otherwise small-sample noise gets reported as a "shift".
TREND_MIN_HISTORY_FOR_CHANGE_POINT = 4
TREND_CHANGE_POINT_MIN_MAGNITUDE = 0.15

# Cognitive distortion analysis settings (Beck/Burns taxonomy)
DISTORTION_MIN_SCORE_TO_REPORT = 0.03
DISTORTION_TOP_N = 3

# Construct-validity audit settings
CONSTRUCT_AUDIT_SAMPLE_SIZE = 300

# Gemini-backed narrative generation (RAG copilot, etc.). Requires GOOGLE_API_KEY to be
# set (see .env.example); callers must treat generation failures as non-fatal and fall
# back to their deterministic/template output, since this is a third-party network call.
GEMINI_MODEL_NAME = "gemini-flash-latest"
GEMINI_REQUEST_TIMEOUT_MS = 10000
GEMINI_MAX_OUTPUT_TOKENS = 1024
