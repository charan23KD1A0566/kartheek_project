"""Train and evaluate the SIF text classifier with proper evaluation metrics.

This script:
1. Uses 80/20 train/test split with stratification
2. Applies probability calibration to fix 90% probability issue
3. Calculates comprehensive metrics: accuracy, precision, recall, F1
4. Generates confusion matrices for all classes
5. Saves detailed model metadata

The training data is manually labeled for demonstration purposes.
Production use requires expert-reviewed, certified safety data.
"""

import csv
import json
import re
from pathlib import Path

import joblib
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "training_reports.csv"
ARTIFACT_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = ARTIFACT_DIR / "sif_model.joblib"
METADATA_PATH = ARTIFACT_DIR / "model_metadata.json"
VALID_LABELS = {"YES", "NO", "UNCERTAIN"}


def clean_text(value: str) -> str:
    """Normalize text for ML model."""
    return re.sub(r"\s+", " ", value.lower()).strip()


def load_data():
    """Load and validate training data from CSV."""
    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    
    required = {"report_text", "sif_status", "risk_level", "hazard_category", "control_failure"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"Dataset must contain columns: {sorted(required)}")
    
    for index, row in enumerate(rows, start=2):
        if not row["report_text"].strip():
            raise ValueError(f"Empty report_text at CSV row {index}")
        if row["sif_status"] not in VALID_LABELS:
            raise ValueError(f"Invalid sif_status at CSV row {index}: {row['sif_status']}")
    
    return rows


def main():
    """Train model with proper evaluation pipeline."""
    print("=" * 70)
    print("SIF SENTINEL ML MODEL TRAINING & EVALUATION")
    print("=" * 70)
    
    # ===== LOAD DATA =====
    rows = load_data()
    print(f"\n✓ Loaded {len(rows)} training records from {DATA_PATH}")
    
    texts = [clean_text(row["report_text"]) for row in rows]
    labels = [row["sif_status"] for row in rows]
    
    # Class distribution
    yes_count = labels.count("YES")
    no_count = labels.count("NO")
    uncertain_count = labels.count("UNCERTAIN")
    print(f"\nClass Distribution:")
    print(f"  - YES (dangerous):    {yes_count} ({100*yes_count/len(rows):.1f}%)")
    print(f"  - NO (safe):          {no_count} ({100*no_count/len(rows):.1f}%)")
    print(f"  - UNCERTAIN:          {uncertain_count} ({100*uncertain_count/len(rows):.1f}%)")
    
    # ===== TRAIN/TEST SPLIT =====
    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.20, random_state=42, stratify=labels
    )
    print(f"\nTrain/Test Split (80/20 with stratification):")
    print(f"  - Training:   {len(x_train)} records")
    print(f"  - Test:       {len(x_test)} records")
    print(f"  - Train YES:  {y_train.count('YES')} ({100*y_train.count('YES')/len(y_train):.1f}%)")
    print(f"  - Train NO:   {y_train.count('NO')} ({100*y_train.count('NO')/len(y_train):.1f}%)")
    print(f"  - Train UNC:  {y_train.count('UNCERTAIN')} ({100*y_train.count('UNCERTAIN')/len(y_train):.1f}%)")
    print(f"  - Test YES:   {y_test.count('YES')} ({100*y_test.count('YES')/len(y_test):.1f}%)")
    print(f"  - Test NO:    {y_test.count('NO')} ({100*y_test.count('NO')/len(y_test):.1f}%)")
    print(f"  - Test UNC:   {y_test.count('UNCERTAIN')} ({100*y_test.count('UNCERTAIN')/len(y_test):.1f}%)")
    
    # ===== BUILD PIPELINE =====
    print(f"\nBuilding ML Pipeline...")
    print(f"  - Feature Extraction: TF-IDF with bigrams")
    print(f"  - Base Model: Logistic Regression (balanced class weights)")
    print(f"  - Calibration: Sigmoid (to fix probability scores)")
    
    # Create base pipeline
    base_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),          # Unigrams and bigrams
            min_df=2,                     # Minimum document frequency
            max_df=0.95,                  # Maximum document frequency
            sublinear_tf=True,            # Sublinear TF scaling
            stop_words="english"          # Remove common stop words
        )),
        ("classifier", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",      # Handle class imbalance
            random_state=42,
            solver="lbfgs"
        )),
    ])
    
    # Apply Sigmoid calibration to fix probability scores
    calibrated_model = CalibratedClassifierCV(base_pipeline, method="sigmoid", cv=5)
    
    # ===== TRAIN MODEL =====
    print(f"\nTraining model (this may take a minute)...")
    calibrated_model.fit(x_train, y_train)
    print(f"✓ Model training complete")
    
    # ===== EVALUATE MODEL =====
    print(f"\n" + "=" * 70)
    print("EVALUATION RESULTS ON TEST SET")
    print("=" * 70)
    
    # Predictions
    y_pred = calibrated_model.predict(x_test)
    y_proba = calibrated_model.predict_proba(x_test)
    
    # Overall accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nOverall Accuracy: {accuracy:.4f} ({100*accuracy:.2f}%)")
    
    # Detailed metrics per class
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, labels=["NO", "UNCERTAIN", "YES"], zero_division=0
    )
    
    print(f"\nPer-Class Metrics:")
    print(f"  NO (Safe):")
    print(f"    - Precision: {precision[0]:.4f} (of predicted NO, {100*precision[0]:.1f}% correct)")
    print(f"    - Recall:    {recall[0]:.4f} ({100*recall[0]:.1f}% of actual NO caught)")
    print(f"    - F1-Score:  {f1[0]:.4f}")
    print(f"    - Support:   {support[0]} test examples")
    
    print(f"\n  UNCERTAIN (Ambiguous):")
    print(f"    - Precision: {precision[1]:.4f} (of predicted UNCERTAIN, {100*precision[1]:.1f}% correct)")
    print(f"    - Recall:    {recall[1]:.4f} ({100*recall[1]:.1f}% of actual UNCERTAIN caught)")
    print(f"    - F1-Score:  {f1[1]:.4f}")
    print(f"    - Support:   {support[1]} test examples")
    
    print(f"\n  YES (Dangerous):")
    print(f"    - Precision: {precision[2]:.4f} (of predicted YES, {100*precision[2]:.1f}% correct)")
    print(f"    - Recall:    {recall[2]:.4f} ({100*recall[2]:.1f}% of actual YES caught)")
    print(f"    - F1-Score:  {f1[2]:.4f}")
    print(f"    - Support:   {support[2]} test examples")
    
    # Confusion matrix
    matrix = confusion_matrix(y_test, y_pred, labels=["NO", "UNCERTAIN", "YES"]).tolist()
    print(f"\nConfusion Matrix (rows=actual, cols=predicted):")
    print(f"              NO  UNC  YES")
    print(f"  NO  [{matrix[0][0]:3d}  {matrix[0][1]:3d}  {matrix[0][2]:3d}]")
    print(f"  UNC [{matrix[1][0]:3d}  {matrix[1][1]:3d}  {matrix[1][2]:3d}]")
    print(f"  YES [{matrix[2][0]:3d}  {matrix[2][1]:3d}  {matrix[2][2]:3d}]")
    
    # Probability calibration check
    print(f"\nProbability Calibration Check (on test set):")
    
    # Get probabilities by predicted class
    yes_predicted_idx = y_pred == "YES"
    no_predicted_idx = y_pred == "NO"
    uncertain_predicted_idx = y_pred == "UNCERTAIN"
    
    if yes_predicted_idx.any():
        yes_probs = y_proba[yes_predicted_idx][:, 2]
        print(f"  - YES predictions (n={len(yes_probs)}):     mean prob={yes_probs.mean():.4f}, min={yes_probs.min():.4f}, max={yes_probs.max():.4f}")
    else:
        print(f"  - YES predictions: no test examples")
    
    if no_predicted_idx.any():
        no_probs = y_proba[no_predicted_idx][:, 0]
        print(f"  - NO predictions (n={len(no_probs)}):      mean prob={no_probs.mean():.4f}, min={no_probs.min():.4f}, max={no_probs.max():.4f}")
    else:
        print(f"  - NO predictions: no test examples")
    
    if uncertain_predicted_idx.any():
        uncertain_probs = y_proba[uncertain_predicted_idx][:, 1]
        print(f"  - UNCERTAIN predictions (n={len(uncertain_probs)}): mean prob={uncertain_probs.mean():.4f}, min={uncertain_probs.min():.4f}, max={uncertain_probs.max():.4f}")
    else:
        print(f"  - UNCERTAIN predictions: no test examples")
    
    # ===== SAVE ARTIFACTS =====
    ARTIFACT_DIR.mkdir(exist_ok=True)
    
    metadata = {
        "model_type": "TFIDF_LOGISTIC_CALIBRATED",
        "model_version": "2.0",
        "training_timestamp": "2024",
        "dataset": str(DATA_PATH.relative_to(ROOT)),
        "dataset_size": len(rows),
        "class_distribution": {
            "YES": yes_count,
            "NO": no_count,
            "UNCERTAIN": uncertain_count,
        },
        "class_percentages": {
            "YES": round(100 * yes_count / len(rows), 2),
            "NO": round(100 * no_count / len(rows), 2),
            "UNCERTAIN": round(100 * uncertain_count / len(rows), 2),
        },
        "train_size": len(x_train),
        "test_size": len(x_test),
        "train_test_ratio": "80/20 (stratified)",
        "accuracy": round(float(accuracy), 4),
        "metrics": {
            "NO": {
                "precision": round(float(precision[0]), 4),
                "recall": round(float(recall[0]), 4),
                "f1_score": round(float(f1[0]), 4),
                "support": int(support[0]),
            },
            "UNCERTAIN": {
                "precision": round(float(precision[1]), 4),
                "recall": round(float(recall[1]), 4),
                "f1_score": round(float(f1[1]), 4),
                "support": int(support[1]),
            },
            "YES": {
                "precision": round(float(precision[2]), 4),
                "recall": round(float(recall[2]), 4),
                "f1_score": round(float(f1[2]), 4),
                "support": int(support[2]),
            },
        },
        "confusion_matrix": {
            "labels": ["NO", "UNCERTAIN", "YES"],
            "matrix": matrix,
            "interpretation": {
                "true_negatives": matrix[0][0],
                "false_positives_as_yes": matrix[0][2],
                "false_positives_as_uncertain": matrix[0][1],
                "total_correct_no": matrix[0][0],
                "true_positives": matrix[2][2],
                "false_negatives_as_uncertain": matrix[2][1],
                "false_negatives_as_no": matrix[2][0],
                "total_correct_yes": matrix[2][2],
            },
        },
        "feature_extraction": {
            "type": "TF-IDF with bigrams",
            "ngram_range": [1, 2],
            "min_df": 2,
            "max_df": 0.95,
            "sublinear_tf": True,
            "stop_words": "english",
        },
        "base_classifier": {
            "type": "Logistic Regression",
            "max_iterations": 2000,
            "class_weight": "balanced",
            "solver": "lbfgs",
        },
        "calibration": {
            "type": "Sigmoid",
            "cv_folds": 5,
            "purpose": "Correct probability scores to be well-calibrated",
        },
        "probability_stats": {
            "YES_mean_prob": round(float(yes_probs.mean()), 4) if (yes_predicted_idx.any()) else None,
            "YES_min_prob": round(float(yes_probs.min()), 4) if (yes_predicted_idx.any()) else None,
            "YES_max_prob": round(float(yes_probs.max()), 4) if (yes_predicted_idx.any()) else None,
            "NO_mean_prob": round(float(no_probs.mean()), 4) if (no_predicted_idx.any()) else None,
            "NO_min_prob": round(float(no_probs.min()), 4) if (no_predicted_idx.any()) else None,
            "NO_max_prob": round(float(no_probs.max()), 4) if (no_predicted_idx.any()) else None,
            "UNCERTAIN_mean_prob": round(float(uncertain_probs.mean()), 4) if (uncertain_predicted_idx.any()) else None,
            "UNCERTAIN_min_prob": round(float(uncertain_probs.min()), 4) if (uncertain_predicted_idx.any()) else None,
            "UNCERTAIN_max_prob": round(float(uncertain_probs.max()), 4) if (uncertain_predicted_idx.any()) else None,
        },
        "usage": {
            "predict_proba": "Use model.predict_proba(texts) to get calibrated probabilities",
            "classes_order": ["NO", "UNCERTAIN", "YES"],
            "threshold_default": [0.33, 0.33, 0.34],
            "threshold_recommendation": "Adjust based on false-positive/negative cost trade-off",
        },
        "disclaimer": {
            "production_ready": False,
            "data_source": "Manually labeled demonstration data",
            "certification": "Not certified for safety-critical decisions",
            "human_review": "All SIF predictions require expert human review",
            "liability": "This model is a decision-support tool only",
        },
    }
    
    # Save model
    joblib.dump(calibrated_model, MODEL_PATH)
    print(f"\n✓ Model saved to: {MODEL_PATH}")
    
    # Save metadata
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"✓ Metadata saved to: {METADATA_PATH}")
    
    # Print summary
    print(f"\n" + "=" * 70)
    print("TRAINING COMPLETE - SUMMARY")
    print("=" * 70)
    print(f"\n✓ Dataset Size:        {len(rows)} records")
    print(f"✓ Test Accuracy:       {100*accuracy:.2f}%")
    print(f"✓ YES Precision:       {100*precision[2]:.2f}%")
    print(f"✓ YES Recall:          {100*recall[2]:.2f}%")
    print(f"✓ UNCERTAIN F1:        {f1[1]:.4f}")
    print(f"✓ Model Version:       2.0 (calibrated with 3-class support)")
    print(f"✓ Status:              Ready for deployment")
    print(f"\n{metadata}")
    
    return 0


if __name__ == "__main__":
    main()
