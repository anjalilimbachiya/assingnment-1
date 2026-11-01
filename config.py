from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "model"
ASSETS_DIR = BASE_DIR / "assets"

ROLL_NO = 52
RANDOM_STATE = 52
KMEANS_K = 6
TARGET_COL = "Churn"
CSV_NAME = "telco_customer_churn.csv"
CSV_PATH = DATA_DIR / CSV_NAME
CLEANED_CSV_PATH = DATA_DIR / "cleaned_telco_churn.csv"

MODEL_FILES = {
    "logistic_regression": MODEL_DIR / "logistic_regression.joblib",
    "decision_tree": MODEL_DIR / "decision_tree.joblib",
    "random_forest": MODEL_DIR / "random_forest.joblib",
    "knn": MODEL_DIR / "knn.joblib",
    "svm": MODEL_DIR / "svm.joblib",
    "final_model": MODEL_DIR / "final_model.joblib",
    "kmeans": MODEL_DIR / "kmeans.joblib",
    "preprocessor": MODEL_DIR / "preprocessor.joblib",
    "metrics": MODEL_DIR / "training_metrics.json",
    "holdout_predictions": MODEL_DIR / "holdout_predictions.csv",
}

THRESHOLD_DEFAULT = 0.5
