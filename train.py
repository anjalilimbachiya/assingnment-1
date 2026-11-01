import json
from pathlib import Path

import joblib
import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from config import RANDOM_STATE, TARGET_COL, KMEANS_K, MODEL_FILES, CSV_PATH, CLEANED_CSV_PATH


def ensure_dirs():
    Path(CSV_PATH.parent).mkdir(parents=True, exist_ok=True)
    Path(MODEL_FILES["final_model"].parent).mkdir(parents=True, exist_ok=True)


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}. Place the Telco churn CSV in {path.parent}.")
    df = pd.read_csv(path)
    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Drop obvious ID-like fields if present
    for col in ["CustomerID", "customerID", "customer_id"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    # Normalise churn column
    if TARGET_COL in df.columns:
        df[TARGET_COL] = df[TARGET_COL].astype(str).str.strip().str.lower().replace({
            "yes": 1,
            "no": 0,
            "true": 1,
            "false": 0,
            "y": 1,
            "n": 0,
            "1": 1,
            "0": 0,
        })
        df[TARGET_COL] = pd.to_numeric(df[TARGET_COL], errors="coerce").fillna(0).astype(int)

    # Fill missing values
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].fillna("Unknown")
        else:
            df[col] = df[col].fillna(df[col].median())

    # Standardize string values
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    return df


def save_cleaned_dataset(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def build_preprocessor(X: pd.DataFrame):
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()

    transformers = []
    if numeric_cols:
        transformers.append((
            "num",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]),
            numeric_cols,
        ))
    if categorical_cols:
        transformers.append((
            "cat",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]),
            categorical_cols,
        ))

    return ColumnTransformer(transformers=transformers, remainder="drop")


def score_model(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }


def train_models(df: pd.DataFrame):
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL].astype(int)

    X_train, X_temp = train_test_split(X, y, test_size=0.30, random_state=RANDOM_STATE, stratify=y)
    X_val, X_test = train_test_split(X_temp, y.iloc[X_temp.index], test_size=0.50, random_state=RANDOM_STATE, stratify=y.iloc[X_temp.index])

    # Correct split labels matching original idx is not necessary for model training
    X_train, y_train = X_train, y.loc[X_train.index]
    X_val, y_val = X_val, y.loc[X_val.index]
    X_test, y_test = X_test, y.loc[X_test.index]

    preprocessor = build_preprocessor(X_train)

    models = {
        "logistic_regression": LogisticRegression(max_iter=5000, random_state=RANDOM_STATE),
        "decision_tree": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE),
        "knn": KNeighborsClassifier(n_neighbors=5),
        "svm": SVC(probability=True, random_state=RANDOM_STATE),
    }

    results = []
    trained = {}

    for name, model in models.items():
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model),
        ])
        pipe.fit(X_train, y_train)
        val_pred = pipe.predict(X_val)
        metrics = score_model(y_val, val_pred)
        metrics["model"] = name
        results.append(metrics)
        trained[name] = pipe

        joblib.dump(pipe, MODEL_FILES[name])

    # Select final model on business metric: maximize recall while keeping precision viable
    def business_score(item):
        return (0.5 * item["recall"]) + (0.3 * item["f1"]) + (0.2 * item["precision"])

    final_record = max(results, key=business_score)
    final_name = final_record["model"]
    final_model = trained[final_name]

    # Retrain on train+val for deployment
    X_train_val = pd.concat([X_train, X_val], axis=0)
    y_train_val = pd.concat([y_train, y_val], axis=0)
    final_model.fit(X_train_val, y_train_val)
    joblib.dump(final_model, MODEL_FILES["final_model"])
    joblib.dump(preprocessor, MODEL_FILES["preprocessor"])

    # Save holdout predictions for threshold analysis
    holdout_pred = final_model.predict_proba(X_test)[:, 1]
    holdout_df = pd.DataFrame({
        "actual": y_test.to_numpy(),
        "probability": holdout_pred,
    })
    holdout_df.to_csv(MODEL_FILES["holdout_predictions"], index=False)

    summary = {
        "models": results,
        "selected_model": final_name,
        "train_rows": len(X_train),
        "val_rows": len(X_val),
        "test_rows": len(X_test),
    }

    with open(MODEL_FILES["metrics"], "w") as f:
        json.dump(summary, f, indent=2)

    return summary, final_model


def train_kmeans(df: pd.DataFrame):
    X = df.drop(columns=[TARGET_COL])
    kmeans = KMeans(n_clusters=KMEANS_K, random_state=RANDOM_STATE, n_init=20)
    labels = kmeans.fit_predict(X)

    out = df.copy()
    out["Segment"] = labels
    joblib.dump(kmeans, MODEL_FILES["kmeans"])
    return out, kmeans


def run_training():
    ensure_dirs()
    df = load_dataset(CSV_PATH)
    cleaned = clean_dataset(df)
    save_cleaned_dataset(cleaned, CLEANED_CSV_PATH)
    summary, model = train_models(cleaned)
    segmented, _ = train_kmeans(cleaned)
    segmented.to_csv(CLEANED_CSV_PATH, index=False)
    return summary
