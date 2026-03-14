import os
import joblib
import pandas as pd

from ..services.feature_vector import build_feature_vector


MODEL_PATH = os.path.join("backend", "ml", "models", "draft_model.joblib")

_MODEL_BUNDLE = None


def load_model():
    global _MODEL_BUNDLE

    if _MODEL_BUNDLE is None:
        _MODEL_BUNDLE = joblib.load(MODEL_PATH)

    return _MODEL_BUNDLE


def predict_good_pick_probability(
    hero: str,
    allies: list[str],
    enemies: list[str],
    target_role: str | None = None,
    ally_slots=None,
) -> float:
    bundle = load_model()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    features = build_feature_vector(
        hero=hero,
        allies=allies,
        enemies=enemies,
        target_role=target_role,
        ally_slots=ally_slots,
    )

    row = {}
    for col in feature_columns:
        row[col] = features.get(col, 0)

    X = pd.DataFrame([row], columns=feature_columns)

    prob = model.predict_proba(X)[0][1]
    return float(prob)


def ml_score_bonus(
    hero: str,
    allies: list[str],
    enemies: list[str],
    target_role: str | None = None,
    ally_slots=None,
) -> tuple[float, list[str]]:
    """
    Convert ML probability into a small bonus for hybrid ranking.
    Keep ML influence limited so it enhances rules instead of overriding them.
    """

    try:
        prob = predict_good_pick_probability(
            hero=hero,
            allies=allies,
            enemies=enemies,
            target_role=target_role,
            ally_slots=ally_slots,
        )
    except Exception:
        return 0.0, []

    score = 0.0
    reasons: list[str] = []

    if prob >= 0.75:
        score += 1.0
        reasons.append("ML model strongly likes this pick")
    elif prob >= 0.60:
        score += 0.6
        reasons.append("ML model supports this pick")
    elif prob >= 0.45:
        score += 0.2

    return round(score, 2), reasons