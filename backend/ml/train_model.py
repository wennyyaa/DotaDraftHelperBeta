import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


DATASET_PATH = "draft_dataset.csv"
MODEL_DIR = "backend/ml/models"
MODEL_PATH = os.path.join(MODEL_DIR, "draft_model.joblib")


def main():
    print("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)

    drop_cols = []
    for col in ["candidate_hero", "label"]:
        if col in df.columns:
            drop_cols.append(col)

    X = df.drop(columns=drop_cols)
    y = df["label"]

    print("Dataset shape:", df.shape)
    print("Feature columns:", len(X.columns))
    print("Positive rate:", round(float(y.mean()), 6))

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print("Training RandomForest model...")

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=8,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    print("\nAccuracy:", round(accuracy_score(y_test, preds), 4))
    print("\nClassification report:")
    print(classification_report(y_test, preds, zero_division=0))

    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(
        {
            "model": model,
            "feature_columns": list(X.columns),
        },
        MODEL_PATH,
    )

    print("\nModel saved to:", MODEL_PATH)
    print("Max predicted probability:", round(float(probs.max()), 4))
    print("Mean predicted probability:", round(float(probs.mean()), 6))


if __name__ == "__main__":
    main()