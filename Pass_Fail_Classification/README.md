# Pass / Fail Classification Pipeline

This project builds a clean machine learning classification pipeline for a pass/fail student dataset.

It is designed to:
- load the dataset from `data/Pass-Fail Data.csv`
- inspect and clean the raw data
- detect the pass/fail target automatically
- train multiple classifiers
- compare them using standard metrics
- save the best model and preprocessing pipeline

## Project structure

```
Pass_Fail_Classification/
├── data/
│   └── Pass-Fail Data.csv
├── model/
│   ├── best_model.pkl
│   ├── preprocessor.pkl
│   ├── metrics.json
│   ├── model_comparison.csv
│   └── data_summary.json
├── train.py
├── pipeline.py
├── config.py
├── requirements.txt
└── README.md
```

## Run the training pipeline

```bash
python train.py
```

## Notes

- The script is designed to work with a CSV dataset containing a pass/fail target column.
- It automatically detects the target column and keeps the preprocessing separate from the model.
- The final saved model is ready for future frontend integration.
