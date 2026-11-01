from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_FOLDER = PROJECT_ROOT / "data"
MODEL_FOLDER = PROJECT_ROOT / "model"
DATASET_PATH = DATA_FOLDER / "Pass-Fail Data.csv"
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5
TARGET_HINTS = (
    "pass",
    "fail",
    "result",
    "status",
    "outcome",
    "target",
    "label",
    "grade",
    "final_result",
    "pass_fail",
)
ID_COLUMN_HINTS = (
    "id",
    "student_id",
    "roll_no",
    "studentid",
    "enrollment",
    "index",
    "name",
    "email",
    "phone",
    "mobile",
)
