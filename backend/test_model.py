"""Regression checks for the trained SIF model and safety interpretation."""

from services.ai_engine import ai_engine

CASES = [
    (
        "safe",
        "Worker completed routine housekeeping in the office. The area was clean, access routes were clear, and no hazards or control failures were observed.",
        "NO",
        "LOW",
    ),
    (
        "electrical",
        "Worker was exposed to an energized electrical conductor while isolation and lockout procedures were not applied.",
        "YES",
        "HIGH",
    ),
    (
        "confined_space",
        "Worker entered a confined space without atmospheric testing and without a gas monitor.",
        "YES",
        "HIGH",
    ),
    (
        "height",
        "Worker performed work at height without proper fall protection and was exposed to an unprotected edge.",
        "YES",
        "HIGH",
    ),
    (
        "safe_ppe",
        "Worker wore the required PPE and completed the assigned task under normal controlled conditions. No hazards were observed.",
        "NO",
        "LOW",
    ),
]


def main():
    probabilities = []
    for name, text, expected_status, expected_risk in CASES:
        result = ai_engine.analyze_report(text)
        probabilities.append(result.sif_probability)
        assert result.model_type.value == "TFIDF_LOGISTIC", name
        assert result.sif_status.value == expected_status, (name, result.sif_status)
        assert result.risk_level.value == expected_risk, (name, result.risk_level)
        print(name, result.sif_status.value, result.risk_level.value, round(result.sif_probability, 4))
    assert max(probabilities) - min(probabilities) > 0.1
    print("MODEL_REGRESSION_OK")


if __name__ == "__main__":
    main()
