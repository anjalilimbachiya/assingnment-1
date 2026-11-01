# TELECOM 360 – AI Customer Retention Platform

This project provides a premium enterprise analytics dashboard for telecom customer retention, built with Streamlit, Plotly, scikit-learn, and pandas.

## What is included
- Data cleaning and preprocessing
- Training for 5 classifiers: Logistic Regression, Decision Tree, Random Forest, KNN, and SVM
- Evaluation with accuracy, precision, recall, F1, and confusion matrix
- Business-priority model selection
- K-Means segmentation with K = 6 using non-Churn features
- Customer-level churn probability and retention offers
- Interactive threshold analysis
- Dataset explorer with CSV export

## Project structure
- `app.py` – Streamlit dashboard
- `config.py` – project configuration and file paths
- `pipeline.py` – preprocessing, model training, segmentation
- `train.py` – training entry point
- `data/` – input dataset and cleaned CSV
- `model/` – trained model artifacts
- `assets/` – visual assets

## Personal settings
- Roll No.: 52
- Random State: 52
- K-Means clusters: 6

## Run the project
```bash
pip install -r requirements.txt
python train.py
streamlit run app.py
```

## Dataset location
Place the Telco churn dataset at:
```text
data/telco_customer_churn.csv
```

## Notes
- Churn is not used as a feature in the clustering step.
- Threshold tuning is based on validation data.
- Final model selection uses a business-priority score based on recall and precision.
