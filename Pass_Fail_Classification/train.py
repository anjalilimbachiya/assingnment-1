import json
from pathlib import Path

import pandas as pd

from pipeline import train_and_evaluate_pipeline


def main():
    print("========================================")
    print("PASS / FAIL CLASSIFICATION MODEL")
    print("========================================")

    result = train_and_evaluate_pipeline()
    best_name = result["best_model"]
    metrics = result["metrics"]

    print(f"\nDataset:\nRows: {result['data_summary']['dataset_shape']['rows']}\nColumns: {result['data_summary']['dataset_shape']['columns']}")
    print(f"Target: {result['target_column']}")
    print(f"Training Samples: {len(result['X_train'])}")
    print(f"Testing Samples: {len(result['X_test'])}")

    print("\n----------------------------------------")
    print("MODEL COMPARISON")
    print("----------------------------------------")
    print(result["comparison"].to_string(index=False))

    print("\n----------------------------------------")
    print("BEST MODEL")
    print("----------------------------------------")
    print(f"Model: {best_name}")
    print(f"Accuracy: {metrics['Accuracy']:.4f}")
    print(f"Precision: {metrics['Precision']:.4f}")
    print(f"Recall: {metrics['Recall']:.4f}")
    print(f"F1 Score: {metrics['F1 Score']:.4f}")
    print(f"ROC-AUC: {metrics['ROC-AUC']:.4f}")
    print("\nModel saved to:")
    print("model/best_model.pkl")
    print("========================================")


if __name__ == "__main__":
    main()
