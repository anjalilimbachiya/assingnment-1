import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from sklearn.metrics import precision_score, recall_score, confusion_matrix

from config import CLEANED_CSV_PATH, MODEL_FILES, TARGET_COL, THRESHOLD_DEFAULT
from pipeline import clean_dataset, load_dataset

st.set_page_config(page_title="TELECOM 360", page_icon="📡", layout="wide")


CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(135deg, #080B12 0%, #0B1220 100%);
        color: #E6F3FF;
    }
    .block-container {
        padding-top: 1rem;
    }
    div[data-testid="stSidebar"] {
        background: rgba(11, 18, 32, 0.9);
        border-right: 1px solid rgba(22, 119, 255, 0.3);
    }
    .card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(0,184,255,0.25);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 0 30px rgba(0,184,255,0.12);
        backdrop-filter: blur(8px);
    }
    .metric-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(22,119,255,0.35);
        border-radius: 14px;
        padding: 14px;
    }
    h1, h2, h3 { color: #EAF6FF; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data
def get_cleaned_df():
    if CLEANED_CSV_PATH.exists():
        return pd.read_csv(CLEANED_CSV_PATH)
    csv_path = CLEANED_CSV_PATH.parent / "telco_customer_churn.csv"
    if not csv_path.exists():
        st.warning("Dataset not found. Put the CSV in data/telco_customer_churn.csv and run train.py again.")
        return pd.DataFrame()
    df = load_dataset(csv_path)
    cleaned = clean_dataset(df)
    cleaned.to_csv(CLEANED_CSV_PATH, index=False)
    return cleaned


def load_model(model_name: str):
    return joblib.load(MODEL_FILES[model_name])


def determine_risk(prob: float):
    if prob >= 0.70:
        return "HIGH"
    if prob >= 0.40:
        return "MEDIUM"
    return "LOW"


def get_retention_offer(risk: str):
    if risk == "HIGH":
        return "25% loyalty discount + proactive retention specialist + 2-month extension"
    if risk == "MEDIUM":
        return "15% loyalty discount + personalized plan review"
    return "5% digital bundle credit + service check-in"


def get_top_risk_factors(row: pd.Series):
    factors = []
    if "Contract" in row and str(row["Contract"]).lower() == "month-to-month":
        factors.append("Month-to-month contract")
    if "Tenure" in row and float(row["Tenure"]) < 12:
        factors.append("Short tenure")
    if "MonthlyCharges" in row and "TotalCharges" in row and float(row["MonthlyCharges"]) > (float(row["TotalCharges"]) / max(1, float(row["Tenure"]))):
        factors.append("Monthly charge pressure")
    if "InternetService" in row and str(row["InternetService"]).lower() in {"fiber optic", "dsl"}:
        factors.append("Service churn risk")
    if "PaymentMethod" in row and str(row["PaymentMethod"]).lower() == "electronic check":
        factors.append("Higher churn payment pattern")
    if "CustomerServiceCalls" in row and int(row["CustomerServiceCalls"]) > 3:
        factors.append("Frequent support calls")
    return factors[:3]


def render_sidebar():
    st.sidebar.markdown("<div class='card'><h3>TELECOM 360</h3><p>AI Customer Retention Platform</p></div>", unsafe_allow_html=True)
    return st.sidebar.radio("Navigation", [
        "Overview",
        "Model Performance",
        "Customer Search",
        "Segment Analytics",
        "Dataset Explorer",
    ])


def render_overview(df: pd.DataFrame):
    st.title("TELECOM 360 – Customer Retention Intelligence")
    if df.empty:
        st.warning("Dataset is missing. Add data/telco_customer_churn.csv and re-run training.")
        return

    churn_rate = df[TARGET_COL].mean() * 100 if TARGET_COL in df.columns else 0
    avg_tenure = df["Tenure"].mean() if "Tenure" in df.columns else 0
    avg_monthly = df["MonthlyCharges"].mean() if "MonthlyCharges" in df.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Churn Rate", f"{churn_rate:.2f}%")
    col2.metric("Average Tenure", f"{avg_tenure:.1f} mo")
    col3.metric("Average Monthly", f"${avg_monthly:.2f}")
    col4.metric("Priority", "Retention focus")

    chart_col, info_col = st.columns([1.5, 1])
    with chart_col:
        churn_counts = df[TARGET_COL].value_counts().reset_index()
        churn_counts.columns = ["Churn", "Customers"]
        fig = px.pie(churn_counts, names="Churn", values="Customers", color_discrete_sequence=["#00B8FF", "#FF1744"])
        st.plotly_chart(fig, use_container_width=True)

    with info_col:
        st.markdown("<div class='card'><h3>Business Strategy</h3><p>Target at-risk customers with the highest churn probability, especially short-tenure and month-to-month contract users.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='card'><h3>Priority Rules</h3><ul><li>Recall over raw accuracy</li><li>Protect precision for campaign efficiency</li><li>Focus on stage-based retention</li></ul></div>", unsafe_allow_html=True)


def render_model_performance():
    st.title("Model Performance")
    if not MODEL_FILES["metrics"].exists():
        st.warning("Train the model first: run python train.py")
        return

    with open(MODEL_FILES["metrics"]) as f:
        summary = json.load(f)

    model_df = pd.DataFrame(summary["models"])
    st.dataframe(model_df[["model", "accuracy", "precision", "recall", "f1"]], use_container_width=True)

    threshold = st.slider("Prediction Threshold", 0.30, 0.85, THRESHOLD_DEFAULT, step=0.01)
    if MODEL_FILES["holdout_predictions"].exists():
        holdout = pd.read_csv(MODEL_FILES["holdout_predictions"])
        preds = (holdout["probability"] >= threshold).astype(int)
        precision = precision_score(holdout["actual"], preds, zero_division=0)
        recall = recall_score(holdout["actual"], preds, zero_division=0)
        cm = confusion_matrix(holdout["actual"], preds)

        col1, col2, col3 = st.columns(3)
        col1.metric("Precision", f"{precision:.3f}")
        col2.metric("Recall", f"{recall:.3f}")
        col3.metric("Threshold", f"{threshold:.2f}")
        st.write("Confusion Matrix")
        st.write(cm)

    # Visual threshold tradeoff curve
    thresholds = np.linspace(0.30, 0.85, 100)
    precision_curve = []
    recall_curve = []
    if MODEL_FILES["holdout_predictions"].exists():
        holdout = pd.read_csv(MODEL_FILES["holdout_predictions"])
        y_true = holdout["actual"].values
        probs = holdout["probability"].values
        for t in thresholds:
            pred = (probs >= t).astype(int)
            precision_curve.append(precision_score(y_true, pred, zero_division=0))
            recall_curve.append(recall_score(y_true, pred, zero_division=0))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=thresholds, y=precision_curve, mode="lines", name="Precision"))
        fig.add_trace(go.Scatter(x=thresholds, y=recall_curve, mode="lines", name="Recall"))
        fig.update_layout(title="Precision-Recall tradeoff", xaxis_title="Threshold", yaxis_title="Score")
        st.plotly_chart(fig, use_container_width=True)


def render_customer_search(df: pd.DataFrame):
    st.title("Customer Search")
    if df.empty:
        st.warning("No data loaded.")
        return

    search_input = st.text_input("Search by CustomerName or CustomerID")
    if search_input:
        matches = df[df.astype(str).apply(lambda row: row.str.contains(search_input, case=False, na=False)).any(axis=1)]
        if matches.empty:
            st.warning("No matching customer found.")
            return
        customer = matches.iloc[0]
    else:
        customer = df.iloc[0]

    final_model = load_model("final_model")
    feature_df = df.drop(columns=[TARGET_COL], errors="ignore")
    if feature_df.empty:
        st.warning("No valid features found to score this customer.")
        return

    row = feature_df.iloc[[0]].copy()
    if "CustomerName" in customer.index:
        row = customer.drop(labels=[TARGET_COL], errors="ignore").to_frame().T

    prob = final_model.predict_proba(row)[0, 1]
    risk = determine_risk(prob)

    st.subheader(f"Customer: {customer.get('CustomerName', customer.get('customerID', 'Unknown'))}")
    st.metric("Churn Probability", f"{prob:.3f}")
    st.metric("Risk Level", risk)
    st.write("Top 3 risk factors:")
    for factor in get_top_risk_factors(customer):
        st.write(f"- {factor}")
    st.write("Personalized retention offer:")
    st.success(get_retention_offer(risk))

    st.json(customer.to_dict())


def render_segment_analytics(df: pd.DataFrame):
    st.title("Segment Analytics")
    if df.empty:
        st.warning("No data loaded.")
        return

    if "Segment" not in df.columns:
        kmeans = joblib.load(MODEL_FILES["kmeans"])
        features = df.drop(columns=[TARGET_COL], errors="ignore")
        df = df.copy()
        df["Segment"] = kmeans.predict(features)

    seg_dist = df["Segment"].value_counts().reset_index()
    seg_dist.columns = ["Segment", "Customers"]
    fig1 = px.bar(seg_dist, x="Segment", y="Customers", color="Segment", color_continuous_scale="Blues")
    st.plotly_chart(fig1, use_container_width=True)

    churn_by_segment = df.groupby("Segment", as_index=False)[TARGET_COL].mean().rename(columns={TARGET_COL: "ChurnRate"})
    fig2 = px.bar(churn_by_segment, x="Segment", y="ChurnRate", color="Segment")
    st.plotly_chart(fig2, use_container_width=True)

    if "Contract" in df.columns:
        contract_df = df.groupby(["Contract", TARGET_COL]).size().reset_index(name="Customers")
        fig3 = px.bar(contract_df, x="Contract", y="Customers", color=TARGET_COL, barmode="stack")
        st.plotly_chart(fig3, use_container_width=True)

    if "Tenure" in df.columns:
        tenure_df = df.groupby("Tenure", as_index=False)[TARGET_COL].mean().rename(columns={TARGET_COL: "ChurnRate"})
        fig4 = px.line(tenure_df, x="Tenure", y="ChurnRate", markers=True)
        st.plotly_chart(fig4, use_container_width=True)


def render_dataset_explorer(df: pd.DataFrame):
    st.title("Dataset Explorer")
    if df.empty:
        st.warning("No dataset available.")
        return

    st.dataframe(df.head(200), use_container_width=True)
    csv_data = df.to_csv(index=False)
    st.download_button("Download cleaned CSV", csv_data, file_name="cleaned_telco_churn.csv", mime="text/csv")


def main():
    df = get_cleaned_df()
    page = render_sidebar()

    if page == "Overview":
        render_overview(df)
    elif page == "Model Performance":
        render_model_performance()
    elif page == "Customer Search":
        render_customer_search(df)
    elif page == "Segment Analytics":
        render_segment_analytics(df)
    else:
        render_dataset_explorer(df)


if __name__ == "__main__":
    main()
