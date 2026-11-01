import json
import os
from pathlib import Path

import joblib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

import config

matplotlib.use("Agg")


def ensure_directories():
    config.DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    config.MODEL_FOLDER.mkdir(parents=True, exist_ok=True)


def normalize_string(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def is_target_like_column(series):
    values = series.dropna().astype(str).str.strip().tolist()
    if not values:
        return False
    normalized = {normalize_string(v) for v in values}
    positive = {"pass", "p", "true", "yes", "1", "passed", "success", "eligible"}
    negative = {"fail", "f", "false", "no", "0", "failed", "unsuccessful"}
    overlap = normalized & (positive | negative)
    return len(overlap) >= 1 and len(normalized) <= 10


def detect_target_column(df):
    for col in df.columns:
        col_name = normalize_string(col)
        if any(hint in col_name for hint in config.TARGET_HINTS):
            if is_target_like_column(df[col]):
                return col

    for col in df.columns:
        if is_target_like_column(df[col]):
            return col

    raise ValueError("Could not identify a valid pass/fail target column automatically.")


def convert_target(values):
    mapped = []
    for value in values:
        text = normalize_string(value)
        if text in {"pass", "passed", "p", "true", "yes", "1", "success", "successful"}:
            mapped.append(1)
        elif text in {"fail", "failed", "f", "false", "no", "0", "unsuccessful"}:
            mapped.append(0)
        elif text in {"pass", "fail"}:
            mapped.append(1 if text == "pass" else 0)
        else:
            mapped.append(np.nan)
    return pd.Series(mapped, index=values.index)


def infer_cleaning_actions(df):
    actions = []
    if df.duplicated().any():
        actions.append("Removed duplicate rows.")
    for col in df.columns:
        if df[col].isnull().any():
            actions.append(f"Handled missing values in '{col}'.")
    for col in df.columns:
        if df[col].dtype == object:
            empty_count = df[col].astype(str).str.strip().eq("").sum()
            if empty_count > 0:
                actions.append(f"Replaced empty strings in '{col}' with missing values.")
    return actions


def analyze_dataset(df, target_column):
    summary = {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "numerical_columns": [],
        "categorical_columns": [],
        "unique_values": {col: int(df[col].nunique(dropna=True)) for col in df.columns},
        "target_column": target_column,
    }

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            summary["numerical_columns"].append(col)
        else:
            summary["categorical_columns"].append(col)

    return summary


def clean_dataframe(df, target_column):
    cleaned = df.copy()
    cleaned.columns = [str(col).strip() for col in cleaned.columns]

    if target_column not in cleaned.columns:
        raise ValueError(f"Target column '{target_column}' not found after cleaning.")

    for col in cleaned.columns:
        cleaned[col] = cleaned[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        cleaned[col] = cleaned[col].replace(r"^\s*$", np.nan, regex=True)

    for col in cleaned.columns:
        if pd.api.types.is_object_dtype(cleaned[col]) or pd.api.types.is_string_dtype(cleaned[col]):
            cleaned[col] = cleaned[col].replace({"N/A": np.nan, "NA": np.nan, "nan": np.nan, "null": np.nan})

    cleaned = cleaned.drop_duplicates()

    for col in cleaned.columns:
        if col == target_column:
            continue
        if cleaned[col].dtype == object:
            cleaned[col] = cleaned[col].astype(str)
        numeric_candidate = pd.to_numeric(cleaned[col], errors="coerce")
        if numeric_candidate.notna().sum() > 0 and numeric_candidate.notna().sum() >= max(1, int(0.8 * len(cleaned))):
            cleaned[col] = numeric_candidate

    cleaned[target_column] = convert_target(cleaned[target_column])
    cleaned = cleaned.dropna(subset=[target_column]).reset_index(drop=True)

    for col in list(cleaned.columns):
        if col.lower() in {"student_id", "student id", "id", "roll no", "roll_no", "name", "email", "phone", "mobile"}:
            cleaned = cleaned.drop(columns=[col])

    return cleaned


def make_preprocessor(X_train):
    numeric_features = [col for col in X_train.columns if pd.api.types.is_numeric_dtype(X_train[col])]
    categorical_features = [col for col in X_train.columns if col not in numeric_features]

    transformers = []
    if numeric_features:
        numeric_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])
        transformers.append(("num", numeric_pipeline, numeric_features))

    if categorical_features:
        categorical_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ])
        transformers.append(("cat", categorical_pipeline, categorical_features))

    if not transformers:
        raise ValueError("No valid feature columns were found for preprocessing.")

    return ColumnTransformer(transformers=transformers, remainder="drop")


def build_pipeline(model):
    return Pipeline(steps=[("preprocessor", None), ("model", model)])


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = None

    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
    elif hasattr(model, "decision_function"):
        y_prob = model.decision_function(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    confusion = confusion_matrix(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob) if y_prob is not None else np.nan

    return {
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "ROC-AUC": roc_auc,
        "Confusion Matrix": confusion,
    }


def define_models():
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=config.RANDOM_STATE),
        "Decision Tree": DecisionTreeClassifier(random_state=config.RANDOM_STATE),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=config.RANDOM_STATE),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "SVM": SVC(probability=True, random_state=config.RANDOM_STATE),
        "Gradient Boosting": GradientBoostingClassifier(random_state=config.RANDOM_STATE),
    }


def ensure_dataset_exists():
    if not config.DATASET_PATH.exists():
        ensure_directories()
        np.random.seed(config.RANDOM_STATE)
        n = 500
        student_id = np.arange(1, n + 1)
        age = np.random.randint(16, 25, n)
        study_hours = np.random.randint(1, 11, n)
        attendance = np.random.randint(50, 101, n)
        previous_score = np.random.randint(40, 101, n)
        assignment_score = np.random.randint(35, 101, n)
        quiz_score = np.random.randint(30, 101, n)
        sleep_hours = np.random.randint(4, 10, n)
        family_income = np.random.choice(["Low", "Medium", "High"], n)
        gender = np.random.choice(["Male", "Female"], n)
        scholarship = np.random.choice(["Yes", "No"], n)
        residence = np.random.choice(["Hostel", "Day Scholar"], n)
        learning_style = np.random.choice(["Visual", "Auditory", "Kinesthetic"], n)

        scores = (
            0.5 * study_hours
            + 0.4 * attendance
            + 0.6 * previous_score
            + 0.5 * assignment_score
            + 0.4 * quiz_score
            + 0.8 * np.where(sleep_hours >= 7, 1, 0)
            + 0.3 * np.where(family_income == "High", 1, 0)
            + 0.2 * np.where(gender == "Female", 1, 0)
            + 0.2 * np.where(scholarship == "Yes", 1, 0)
        )

        probability = 1 / (1 + np.exp(-(scores - 190) / 30))
        pass_label = (np.random.rand(n) < probability).astype(int)

        df = pd.DataFrame({
            "Student_ID": student_id,
            "Age": age,
            "Gender": gender,
            "Study_Hours": study_hours,
            "Attendance": attendance,
            "Previous_Score": previous_score,
            "Assignment_Score": assignment_score,
            "Quiz_Score": quiz_score,
            "Sleep_Hours": sleep_hours,
            "Family_Income": family_income,
            "Scholarship": scholarship,
            "Residence": residence,
            "Learning_Style": learning_style,
            "Pass/Fail": np.where(pass_label == 1, "Pass", "Fail"),
        })
        df.to_csv(config.DATASET_PATH, index=False)
        return df

    return pd.read_csv(config.DATASET_PATH)


def create_model_comparison_table(results):
    comparison = []
    for name, metrics in results.items():
        comparison.append({
            "Model": name,
            "Accuracy": metrics["Accuracy"],
            "Precision": metrics["Precision"],
            "Recall": metrics["Recall"],
            "F1 Score": metrics["F1 Score"],
            "ROC_AUC": metrics["ROC-AUC"],
        })

    df = pd.DataFrame(comparison)
    df = df.sort_values(by=["F1 Score", "Recall", "Accuracy"], ascending=[False, False, False]).reset_index(drop=True)
    return df


def select_best_model(results):
    ranked = sorted(results.items(), key=lambda x: (-x[1]["F1 Score"], -x[1]["Recall"], -x[1]["Accuracy"]))
    return ranked[0]


def save_json(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)


def save_model_outputs(model_name, final_pipeline, metrics, comparison_df, data_summary, X_train, y_train, target_column):
    joblib.dump(final_pipeline, config.MODEL_FOLDER / "best_model.pkl")
    joblib.dump(final_pipeline.named_steps["preprocessor"], config.MODEL_FOLDER / "preprocessor.pkl")

    metrics_payload = {
        "best_model_name": model_name,
        "accuracy": metrics["Accuracy"],
        "precision": metrics["Precision"],
        "recall": metrics["Recall"],
        "f1_score": metrics["F1 Score"],
        "roc_auc": metrics["ROC-AUC"],
        "training_rows": int(len(X_train)),
        "testing_rows": int(len(y_train)),
        "feature_names": list(X_train.columns),
        "target_column": target_column,
        "random_state": config.RANDOM_STATE,
        "test_size": config.TEST_SIZE,
        "cross_validation_results": data_summary.get("cross_validation", {}),
    }
    save_json(config.MODEL_FOLDER / "metrics.json", metrics_payload)

    comparison_df.to_csv(config.MODEL_FOLDER / "model_comparison.csv", index=False)
    save_json(config.MODEL_FOLDER / "data_summary.json", data_summary)


def train_and_evaluate_pipeline():
    ensure_directories()
    raw_df = ensure_dataset_exists()
    target_column = detect_target_column(raw_df)
    print("Dataset Shape:")
    print(f"Rows: {raw_df.shape[0]} | Columns: {raw_df.shape[1]}")
    print(f"Target Column: {target_column}")

    cleaned_df = clean_dataframe(raw_df.copy(), target_column)
    print("\nInitial cleaning summary:")
    for action in infer_cleaning_actions(raw_df):
        print("-", action)

    if cleaned_df.empty:
        raise ValueError("Dataset is empty after cleaning. Cannot train the model.")

    if cleaned_df[target_column].nunique() != 2:
        raise ValueError(f"Target column '{target_column}' must have exactly 2 classes for binary classification.")

    print(f"Target distribution: {cleaned_df[target_column].value_counts().to_dict()}")

    X = cleaned_df.drop(columns=[target_column])
    y = cleaned_df[target_column].astype(int)

    for col in X.columns:
        if any(hint in col.lower() for hint in config.ID_COLUMN_HINTS):
            X = X.drop(columns=[col])
            print(f"Removed identifier-like column '{col}' because it provides no useful predictive value.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE, stratify=y
    )

    print(f"\nTrain/test split -> Train: {len(X_train)}, Test: {len(X_test)}")

    preprocessor = make_preprocessor(X_train)
    model_results = {}
    cross_validation_results = {}

    for name, model in define_models().items():
        pipeline = Pipeline([("preprocessor", preprocessor), ("model", clone(model))])
        pipeline.fit(X_train, y_train)

        metrics = evaluate_model(pipeline, X_test, y_test)
        model_results[name] = metrics

        cv = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.RANDOM_STATE)
        train_pipeline = Pipeline([("preprocessor", make_preprocessor(X_train)), ("model", clone(model))])
        scoring = {
            "accuracy": "accuracy",
            "precision": "precision",
            "recall": "recall",
            "f1": "f1",
        }
        cv_scores = cross_val_score(train_pipeline, X_train, y_train, cv=cv, scoring="f1")
        cross_validation_results[name] = {
            "mean_f1": float(np.mean(cv_scores)),
            "mean_accuracy": float(np.mean(cross_val_score(train_pipeline, X_train, y_train, cv=cv, scoring="accuracy"))),
            "mean_precision": float(np.mean(cross_val_score(train_pipeline, X_train, y_train, cv=cv, scoring="precision"))),
            "mean_recall": float(np.mean(cross_val_score(train_pipeline, X_train, y_train, cv=cv, scoring="recall"))),
        }

    comparison_df = create_model_comparison_table(model_results)
    best_name, best_metrics = select_best_model(model_results)

    final_preprocessor = make_preprocessor(X_train)
    final_preprocessor.fit(X_train)
    final_model = clone(dict(define_models())[best_name])
    final_model.fit(final_preprocessor.transform(X_train), y_train)
    final_pipeline = Pipeline([
        ("preprocessor", final_preprocessor),
        ("model", final_model),
    ])
    final_pipeline.fit(X_train, y_train)

    data_summary = {
        "dataset_shape": {"rows": int(raw_df.shape[0]), "columns": int(raw_df.shape[1])},
        "feature_names": list(X.columns),
        "numerical_features": [col for col in X.columns if pd.api.types.is_numeric_dtype(X[col])],
        "categorical_features": [col for col in X.columns if not pd.api.types.is_numeric_dtype(X[col])],
        "target_column": target_column,
        "missing_values_before_cleaning": raw_df.isnull().sum().to_dict(),
        "missing_values_after_cleaning": cleaned_df.isnull().sum().to_dict(),
        "duplicate_count": int(raw_df.duplicated().sum()),
        "target_distribution": cleaned_df[target_column].value_counts().sort_index().to_dict(),
        "cross_validation": cross_validation_results,
    }

    save_model_outputs(
        best_name,
        final_pipeline,
        best_metrics,
        comparison_df,
        data_summary,
        X_train,
        y_train,
        target_column,
    )

    print("\n=== MODEL COMPARISON ===")
    print(comparison_df.to_string(index=False))
    print(f"\nBEST MODEL: {best_name}")
    print(f"Accuracy: {best_metrics['Accuracy']:.4f}")
    print(f"Precision: {best_metrics['Precision']:.4f}")
    print(f"Recall: {best_metrics['Recall']:.4f}")
    print(f"F1 Score: {best_metrics['F1 Score']:.4f}")
    print(f"ROC-AUC: {best_metrics['ROC-AUC']:.4f}")

    print("\nSaved model files:")
    for file_name in ["best_model.pkl", "preprocessor.pkl", "metrics.json", "model_comparison.csv", "data_summary.json"]:
        print(f"- {config.MODEL_FOLDER / file_name}")

    return {
        "best_model": best_name,
        "metrics": best_metrics,
        "comparison": comparison_df,
        "data_summary": data_summary,
        "target_column": target_column,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
    }
