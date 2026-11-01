# Model Card: TELECOM 360 Retention Model

## Model purpose
This model predicts customer churn risk to support proactive retention interventions.

## Candidate models
- Logistic Regression
- Decision Tree
- Random Forest
- K-Nearest Neighbors
- Support Vector Machine

## Final selection criteria
The final model is selected using a business-priority metric that prioritizes strong recall while preserving precision and F1.

## Data handling
- Missing values are filled using data-aware methods.
- Numeric and categorical features are processed separately.
- Churn is excluded from clustering features.
- Prevented data leakage by using validation and hold-out splits for evaluation.

## Deployment notes
The trained models and summary outputs are stored in the `model/` folder.

## Risk interpretation
- LOW: healthy customer profile
- MEDIUM: monitor customer and run targeted outreach
- HIGH: immediate retention action recommended
