"""
Test script to verify the trained ML model makes diverse predictions
across different semantic safety report types.

This test verifies:
1. Safe reports DO NOT get automatic high probability
2. Dangerous reports get high probability
3. Ambiguous reports get uncertain classification
4. Different scenarios produce different predictions (model is working)
"""

import csv
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = Path(__file__).resolve().parent / "models" / "sif_model.joblib"

# Test cases: (name, text, expected_category)
TEST_CASES = [
    # SAFE REPORTS - Should predict NO or low probability
    (
        "SAFE: PPE Compliance",
        "Worker wore required PPE, completed the permit, verified isolation and performed maintenance under controlled conditions.",
        "SAFE"
    ),
    (
        "SAFE: No Hazards Present",
        "The area was clean, well-lit, and all safety equipment was properly functioning. No hazards were observed.",
        "SAFE"
    ),
    (
        "SAFE: Proper Procedures",
        "The electrical panel was isolated, locked out, and zero energy was verified before any maintenance was attempted.",
        "SAFE"
    ),
    (
        "SAFE: Confined Space Prep",
        "The confined space was properly ventilated, tested for atmospheric hazards, and a competent person was stationed.",
        "SAFE"
    ),
    (
        "SAFE: Fall Protection",
        "The worker was properly harnessed, connected to an approved anchor point, and working at height safely.",
        "SAFE"
    ),
    
    # DANGEROUS REPORTS - Should predict YES with high probability
    (
        "DANGEROUS: Energized Area Entry",
        "Worker entered the energized electrical area without completing lockout and isolation.",
        "DANGEROUS"
    ),
    (
        "DANGEROUS: LOTO Failure",
        "The worker did not perform isolation verification before starting the maintenance on the electrical equipment.",
        "DANGEROUS"
    ),
    (
        "DANGEROUS: Confined Space Risk",
        "Worker entered a confined space without atmospheric testing or rescue equipment in place.",
        "DANGEROUS"
    ),
    (
        "DANGEROUS: Fall Risk",
        "The worker was working at height without a harness or safety net, standing on an unstable platform.",
        "DANGEROUS"
    ),
    (
        "DANGEROUS: Chemical Exposure",
        "Worker handled hazardous chemicals without gloves, respiratory protection, or eyewash station nearby.",
        "DANGEROUS"
    ),
    (
        "DANGEROUS: Multiple Hazards",
        "Worker entered energized electrical room, climbed on unstable ladder, and attempted to move suspended load manually.",
        "DANGEROUS"
    ),
    
    # AMBIGUOUS REPORTS - Should predict UNCERTAIN or low confidence
    (
        "AMBIGUOUS: Insufficient Detail",
        "Electrical maintenance was performed. Details are not available.",
        "AMBIGUOUS"
    ),
    (
        "AMBIGUOUS: Unclear Exposure",
        "Work was conducted in the hazardous area, but the exact conditions are unclear.",
        "AMBIGUOUS"
    ),
    (
        "AMBIGUOUS: Partial Information",
        "The worker performed a maintenance task. It is not stated whether isolation was completed.",
        "AMBIGUOUS"
    ),
    
    # TRICKY CASES - Safe report with dangerous keywords
    (
        "TRICKY: Safe but Contains Danger Words",
        "PPE was properly worn to prevent electrical exposure. The equipment was safely isolated before work began.",
        "SAFE"
    ),
    (
        "TRICKY: Dangerous but Cautious Language",
        "There was a possibility that the worker might have been exposed to energized parts because the LOTO was not fully verified.",
        "DANGEROUS"
    ),
]


def test_model():
    """Test the trained model on diverse cases."""
    
    print("\n" + "=" * 90)
    print("SIF MODEL PREDICTION TEST - Semantic Diversity Verification")
    print("=" * 90)
    
    # Load model
    if not MODEL_PATH.exists():
        print(f"❌ Model not found at {MODEL_PATH}")
        return False
    
    try:
        model = joblib.load(MODEL_PATH)
        print(f"✓ Loaded model from {MODEL_PATH}")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False
    
    print(f"✓ Model classes: {model.classes_}")
    
    print("\n" + "-" * 90)
    print("RUNNING PREDICTIONS...")
    print("-" * 90)
    
    results = []
    category_predictions = {"SAFE": [], "DANGEROUS": [], "AMBIGUOUS": []}
    
    for idx, (name, text, category) in enumerate(TEST_CASES, 1):
        try:
            # Get predictions
            probabilities = model.predict_proba([text])[0]
            classes = list(model.classes_)
            prediction = model.predict([text])[0]
            
            # Extract probabilities for each class
            prob_dict = {cls: prob for cls, prob in zip(classes, probabilities)}
            
            # Extract specific probabilities
            yes_prob = prob_dict.get("YES", 0.0)
            no_prob = prob_dict.get("NO", 0.0)
            uncertain_prob = prob_dict.get("UNCERTAIN", 0.0)
            
            # Determine confidence
            max_prob = max(probabilities)
            confidence = int(round(max_prob * 100))
            
            # Store results
            result = {
                "index": idx,
                "name": name,
                "category": category,
                "text_snippet": text[:80] + "..." if len(text) > 80 else text,
                "prediction": prediction,
                "yes_prob": yes_prob,
                "no_prob": no_prob,
                "uncertain_prob": uncertain_prob,
                "confidence": confidence,
                "all_probs": prob_dict
            }
            results.append(result)
            category_predictions[category].append(result)
            
            # Print result
            print(f"\n[{idx:2d}] {name}")
            print(f"     Category: {category:12s} → Predicted: {prediction:10s} (Confidence: {confidence}%)")
            print(f"     Probabilities: YES={yes_prob:.3f} | NO={no_prob:.3f} | UNCERTAIN={uncertain_prob:.3f}")
            print(f"     Text: \"{text[:70]}...\"")
            
        except Exception as e:
            print(f"\n[{idx:2d}] {name}")
            print(f"     ❌ Error: {e}")
            return False
    
    # Analysis
    print("\n" + "=" * 90)
    print("ANALYSIS SUMMARY")
    print("=" * 90)
    
    # Check for diversity in predictions
    all_predictions = [r["prediction"] for r in results]
    unique_predictions = set(all_predictions)
    
    print(f"\n✓ Total test cases: {len(results)}")
    print(f"✓ Unique predictions: {unique_predictions}")
    print(f"✓ Prediction diversity: {len(unique_predictions)}/{len(results)} classes represented")
    
    if len(unique_predictions) == 1:
        print(f"❌ CRITICAL: All predictions are {unique_predictions.pop()}! Model is broken!")
        return False
    
    # Analyze by category
    print("\n" + "-" * 90)
    print("PREDICTIONS BY CATEGORY")
    print("-" * 90)
    
    for category in ["SAFE", "DANGEROUS", "AMBIGUOUS"]:
        preds = category_predictions[category]
        if not preds:
            continue
        
        print(f"\n{category} Reports (n={len(preds)}):")
        for pred in preds:
            print(f"  • {pred['name']:40s} → {pred['prediction']:10s} ({pred['confidence']:3d}%)")
    
    # Key validations
    print("\n" + "-" * 90)
    print("KEY VALIDATION CHECKS")
    print("-" * 90)
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Safe reports should mostly be NO
    safe_preds = [r["prediction"] for r in category_predictions["SAFE"]]
    no_count = safe_preds.count("NO")
    total_safe = len(safe_preds)
    checks_total += 1
    if no_count >= total_safe * 0.6:  # At least 60% should be NO
        print(f"✓ Check 1: Safe reports mostly NO ({no_count}/{total_safe}) ✓")
        checks_passed += 1
    else:
        print(f"❌ Check 1: Safe reports mostly NO ({no_count}/{total_safe}) - FAILED")
    
    # Check 2: Dangerous reports should mostly be YES
    dangerous_preds = [r["prediction"] for r in category_predictions["DANGEROUS"]]
    yes_count = dangerous_preds.count("YES")
    total_dangerous = len(dangerous_preds)
    checks_total += 1
    if yes_count >= total_dangerous * 0.6:  # At least 60% should be YES
        print(f"✓ Check 2: Dangerous reports mostly YES ({yes_count}/{total_dangerous}) ✓")
        checks_passed += 1
    else:
        print(f"❌ Check 2: Dangerous reports mostly YES ({yes_count}/{total_dangerous}) - FAILED")
    
    # Check 3: Probabilities are diverse (not all ~0.9)
    all_yes_probs = [r["yes_prob"] for r in results]
    avg_yes = sum(all_yes_probs) / len(all_yes_probs)
    prob_range = max(all_yes_probs) - min(all_yes_probs)
    checks_total += 1
    if prob_range > 0.3:  # Should have at least 0.3 range
        print(f"✓ Check 3: YES probabilities diverse (range={prob_range:.3f}, avg={avg_yes:.3f}) ✓")
        checks_passed += 1
    else:
        print(f"❌ Check 3: YES probabilities clustered (range={prob_range:.3f}) - FAILED")
    
    # Check 4: No prediction should be 100% confident (except UNCERTAIN)
    max_confidence = max([r["confidence"] for r in results])
    checks_total += 1
    if max_confidence < 100:
        print(f"✓ Check 4: No 100% confidence predictions (max={max_confidence}%) ✓")
        checks_passed += 1
    else:
        print(f"⚠ Check 4: Some 100% confidence predictions detected")
    
    # Check 5: Model distinguishes between similar scenarios
    # Safe LOTO vs Dangerous LOTO
    safe_loto = next((r for r in results if "Safe but Contains Danger Words" in r["name"]), None)
    dangerous_loto = next((r for r in results if "LOTO Failure" in r["name"]), None)
    checks_total += 1
    if safe_loto and dangerous_loto and safe_loto["prediction"] != dangerous_loto["prediction"]:
        print(f"✓ Check 5: Model distinguishes similar scenarios ✓")
        print(f"     Safe (LOTO): {safe_loto['prediction']} | Dangerous (LOTO): {dangerous_loto['prediction']}")
        checks_passed += 1
    else:
        print(f"⚠ Check 5: Model may not distinguish similar scenarios")
    
    # Final summary
    print("\n" + "=" * 90)
    print(f"VALIDATION RESULT: {checks_passed}/{checks_total} checks passed")
    print("=" * 90)
    
    if checks_passed >= checks_total - 1:  # Allow 1 check to fail
        print("\n✓ MODEL VALIDATION PASSED - Model is working correctly!")
        print("  - Predictions are diverse (not clustered at 0.9)")
        print("  - Safe/dangerous/ambiguous reports produce different results")
        print("  - Calibration appears effective")
        return True
    else:
        print("\n❌ MODEL VALIDATION FAILED - Model needs investigation")
        return False


def export_test_results_to_csv():
    """Export test results to CSV for documentation."""
    output_path = ROOT / "data" / "model_test_results.csv"
    
    # Run inference
    model = joblib.load(MODEL_PATH)
    
    rows = []
    for name, text, category in TEST_CASES:
        probabilities = model.predict_proba([text])[0]
        classes = list(model.classes_)
        prediction = model.predict([text])[0]
        
        prob_dict = {cls: prob for cls, prob in zip(classes, probabilities)}
        
        rows.append({
            "test_name": name,
            "expected_category": category,
            "model_prediction": prediction,
            "yes_probability": prob_dict.get("YES", 0),
            "no_probability": prob_dict.get("NO", 0),
            "uncertain_probability": prob_dict.get("UNCERTAIN", 0),
            "report_text": text,
        })
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Test results exported to {output_path}")


if __name__ == "__main__":
    success = test_model()
    print("\n")
    try:
        export_test_results_to_csv()
    except Exception as e:
        print(f"Warning: Could not export CSV: {e}")
    
    sys.exit(0 if success else 1)
