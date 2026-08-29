"""
FINAL 10-CASE AI SANITY TEST
Rigorous semantic differentiation testing of trained SIF model

This script tests the ACTUAL TRAINED MODEL through the API
to determine if it responds differently to different safety-report meanings.

DO NOT modify expectations or hardcode results.
Test the real model behavior.
"""

import requests
import json
import time
from datetime import datetime
from statistics import mean, stdev

API_URL = "http://localhost:8000"
DEFAULT_EMAIL = "admin@sifsentinel.demo"
DEFAULT_PASSWORD = "Admin@123"

# Test cases with explicit semantic requirements
TEST_CASES = [
    {
        "id": 1,
        "name": "SAFE ELECTRICAL WORK",
        "text": "Electrical maintenance was performed after the equipment was isolated, locked out and tagged. Zero energy was verified before the worker started the task.",
        "expected_semantic": "SAFE / NO SIF",
        "explanation": "Model should recognize effective controls (isolation + lockout + zero energy verification)"
    },
    {
        "id": 2,
        "name": "DANGEROUS ELECTRICAL EXPOSURE",
        "text": "Worker entered an energized electrical area without completing lockout and isolation. The equipment remained energized while maintenance was being performed.",
        "expected_semantic": "DANGEROUS / SIF YES / HIGH OR CRITICAL",
        "explanation": "Model should identify: energized equipment, exposure, missing isolation, LOTO failure"
    },
    {
        "id": 3,
        "name": "SAFE CONFINED SPACE PREPARATION",
        "text": "The confined-space entry permit was approved before work. Atmospheric testing was completed, ventilation was established, and the rescue plan and trained attendant were confirmed.",
        "expected_semantic": "SAFE / NO SIF",
        "explanation": "Must NOT interpret presence of 'confined space', 'atmospheric testing', 'rescue plan' as automatically dangerous"
    },
    {
        "id": 4,
        "name": "DANGEROUS CONFINED SPACE ENTRY",
        "text": "Worker entered a confined space without atmospheric testing or an approved permit. No trained attendant or rescue arrangement was available.",
        "expected_semantic": "DANGEROUS / SIF YES / HIGH OR CRITICAL",
        "explanation": "Should identify: confined-space entry, no atmospheric testing, permit failure, missing rescue controls"
    },
    {
        "id": 5,
        "name": "SAFE WORKING AT HEIGHT",
        "text": "Worker performed roof maintenance using inspected scaffolding, complete guardrails and an approved fall-arrest harness. The equipment was inspected before use.",
        "expected_semantic": "SAFE / NO SIF",
        "explanation": "Must distinguish controlled work from fall exposure"
    },
    {
        "id": 6,
        "name": "FALL PROTECTION FAILURE",
        "text": "Worker performed roof work near an unprotected edge without a harness, guardrail or other fall protection system.",
        "expected_semantic": "DANGEROUS / SIF YES / HIGH OR CRITICAL",
        "explanation": "Should identify: working at height, unprotected edge, missing fall protection"
    },
    {
        "id": 7,
        "name": "SAFE LIFTING OPERATION",
        "text": "The lifting zone was barricaded and access was restricted. The crane was inspected and the load was secured before lifting. No person was permitted beneath the suspended load.",
        "expected_semantic": "SAFE / NO SIF",
        "explanation": "Must not classify as dangerous simply because crane/lifting/suspended load appear in text"
    },
    {
        "id": 8,
        "name": "LINE-OF-FIRE EXPOSURE",
        "text": "A suspended load moved over an occupied work area while a worker remained directly underneath it. No exclusion zone or barricade was established.",
        "expected_semantic": "DANGEROUS / SIF YES / HIGH OR CRITICAL",
        "explanation": "Should identify: suspended load, worker underneath, exposure, missing exclusion zone/barrier"
    },
    {
        "id": 9,
        "name": "AMBIGUOUS / INSUFFICIENT INFORMATION",
        "text": "Electrical maintenance activity was observed in the work area. The report does not state whether the equipment was isolated or whether the worker was exposed to hazardous energy.",
        "expected_semantic": "UNCERTAIN or appropriately low-confidence result",
        "explanation": "Should recognize critical information is missing. Do not force YES or NO."
    },
    {
        "id": 10,
        "name": "SAFE REPORT WITH DANGEROUS-SOUNDING KEYWORDS",
        "text": "Worker used PPE while performing routine electrical maintenance. The equipment was isolated before work, the permit was verified, all safeguards were checked, and no hazardous exposure occurred.",
        "expected_semantic": "SAFE / NO SIF",
        "explanation": "MOST IMPORTANT: Must understand CONTEXT. Must NOT blindly classify as dangerous due to safety keywords."
    }
]


def get_auth_token():
    """Authenticate and get access token"""
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json={"email": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Authentication failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None
        
        data = response.json()
        token = data.get("access_token")
        if token:
            print(f"✓ Successfully authenticated as: {DEFAULT_EMAIL}")
            return token
        else:
            print("❌ No access token in response")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None


def run_tests():
    """Execute all 10 test cases and collect results"""
    
    print("=" * 100)
    print("FINAL 10-CASE AI SANITY TEST")
    print("=" * 100)
    print()
    print("Testing the ACTUAL trained SIF model via API")
    print("Model expected location: backend/models/sif_model.joblib")
    print(f"API endpoint: {API_URL}/api/analyze")
    print()
    
    # Authenticate first
    print("Authenticating with backend...")
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate. Cannot continue with tests.")
        return [], []
    
    print()
    print("=" * 100)
    print()
    
    results = []
    probabilities = []
    
    for test in TEST_CASES:
        print(f"\n{'='*100}")
        print(f"TEST {test['id']}: {test['name']}")
        print(f"{'='*100}")
        print(f"\nSemanticExpected: {test['expected_semantic']}")
        print(f"Text Preview: {test['text'][:100]}...")
        print()
        
        try:
            # Call the /api/analyze endpoint with token
            response = requests.post(
                f"{API_URL}/api/analyze",
                json={"text": test["text"]},
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ ERROR: HTTP {response.status_code}")
                print(f"Response: {response.text[:200]}")
                results.append({
                    "test_id": test["id"],
                    "test_name": test["name"],
                    "status": "ERROR",
                    "error": f"HTTP {response.status_code}",
                    "sif_status": None,
                    "sif_probability": None,
                    "confidence": None
                })
                continue
            
            data = response.json()
            
            # Extract key fields
            sif_status = data.get("sif_status", "UNKNOWN")
            sif_probability = float(data.get("sif_probability", 0.0))
            confidence = data.get("confidence", 0)
            risk_level = data.get("risk_level", "UNKNOWN")
            hazards = data.get("hazards", [])
            control_failures = data.get("control_failures", [])
            evidence = data.get("evidence", [])
            explanation = data.get("explanation", "")
            model_type = data.get("model_type", "UNKNOWN")
            model_version = data.get("model_version", "UNKNOWN")
            
            # Record probability for statistics
            probabilities.append(sif_probability)
            
            # Display results
            print(f"✓ SUCCESS")
            print(f"\nAI Analysis Result:")
            print(f"  SIF Status: {sif_status}")
            print(f"  SIF Probability: {sif_probability:.4f} ({int(sif_probability*100)}%)")
            print(f"  Confidence: {confidence}%")
            print(f"  Risk Level: {risk_level}")
            print(f"  Hazards: {hazards}")
            print(f"  Control Failures: {control_failures}")
            print(f"  Evidence Count: {len(evidence)}")
            print(f"  Model Type: {model_type}")
            print(f"  Model Version: {model_version}")
            print(f"\nExplanation: {explanation[:200]}...")
            
            results.append({
                "test_id": test["id"],
                "test_name": test["name"],
                "status": "SUCCESS",
                "sif_status": sif_status,
                "sif_probability": sif_probability,
                "confidence": confidence,
                "risk_level": risk_level,
                "hazards": hazards,
                "control_failures": control_failures,
                "evidence_count": len(evidence),
                "explanation": explanation,
                "model_type": model_type,
                "model_version": model_version
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                "test_id": test["id"],
                "test_name": test["name"],
                "status": "ERROR",
                "error": str(e),
                "sif_probability": None
            })
        
        time.sleep(0.5)  # Rate limiting
    
    return results, probabilities


def analyze_results(results, probabilities):
    """Analyze results for semantic differentiation and probability clustering"""
    
    print("\n\n" + "="*100)
    print("SEMANTIC DIFFERENTIATION ANALYSIS")
    print("="*100)
    
    # Extract results by semantic group
    safe_tests = [r for r in results if r["test_id"] in [1, 3, 5, 7, 10]]
    dangerous_tests = [r for r in results if r["test_id"] in [2, 4, 6, 8]]
    ambiguous_tests = [r for r in results if r["test_id"] in [9]]
    
    print("\n[SAFE REPORTS] (Tests 1, 3, 5, 7, 10)")
    print("-" * 100)
    safe_predictions = []
    for r in safe_tests:
        if r["status"] == "SUCCESS":
            print(f"  Test {r['test_id']} ({r['test_name'][:30]}...)")
            print(f"    → SIF: {r['sif_status']:12} | Probability: {r['sif_probability']:.4f}")
            safe_predictions.append(r["sif_probability"])
    
    print("\n[DANGEROUS REPORTS] (Tests 2, 4, 6, 8)")
    print("-" * 100)
    dangerous_predictions = []
    for r in dangerous_tests:
        if r["status"] == "SUCCESS":
            print(f"  Test {r['test_id']} ({r['test_name'][:30]}...)")
            print(f"    → SIF: {r['sif_status']:12} | Probability: {r['sif_probability']:.4f}")
            dangerous_predictions.append(r["sif_probability"])
    
    print("\n[AMBIGUOUS REPORTS] (Test 9)")
    print("-" * 100)
    for r in ambiguous_tests:
        if r["status"] == "SUCCESS":
            print(f"  Test {r['test_id']} ({r['test_name'][:30]}...)")
            print(f"    → SIF: {r['sif_status']:12} | Probability: {r['sif_probability']:.4f}")
    
    # Semantic differentiation checks
    print("\n\n" + "="*100)
    print("SEMANTIC DIFFERENTIATION CHECKS")
    print("="*100)
    
    # Check 1: Safe vs Dangerous
    print("\n1. SAFE vs DANGEROUS Differentiation")
    print("-" * 100)
    if safe_predictions and dangerous_predictions:
        safe_mean = mean(safe_predictions)
        dangerous_mean = mean(dangerous_predictions)
        print(f"  Safe reports mean probability: {safe_mean:.4f}")
        print(f"  Dangerous reports mean probability: {dangerous_mean:.4f}")
        print(f"  Difference: {abs(dangerous_mean - safe_mean):.4f}")
        
        if dangerous_mean > safe_mean + 0.15:
            print(f"  ✓ PASS: Dangerous reports have meaningfully higher probability")
        else:
            print(f"  ⚠ CONCERN: Dangerous reports should have higher probability")
    
    # Check 2: Test 1 vs Test 2 (safe vs dangerous electrical)
    print("\n2. TEST 1 (Safe Electrical) vs TEST 2 (Dangerous Electrical)")
    print("-" * 100)
    t1 = next((r for r in results if r["test_id"] == 1), None)
    t2 = next((r for r in results if r["test_id"] == 2), None)
    if t1 and t2 and t1["status"] == "SUCCESS" and t2["status"] == "SUCCESS":
        print(f"  Test 1 (safe LOTO): {t1['sif_probability']:.4f}")
        print(f"  Test 2 (dangerous no LOTO): {t2['sif_probability']:.4f}")
        if t1["sif_status"] == "NO" and t2["sif_status"] == "YES":
            print(f"  ✓ PASS: Model correctly distinguishes safe vs dangerous LOTO scenarios")
        else:
            print(f"  ❌ FAIL: Model should distinguish these scenarios differently")
    
    # Check 3: Test 3 vs Test 4 (safe vs dangerous confined space)
    print("\n3. TEST 3 (Safe Confined Space) vs TEST 4 (Dangerous Confined Space)")
    print("-" * 100)
    t3 = next((r for r in results if r["test_id"] == 3), None)
    t4 = next((r for r in results if r["test_id"] == 4), None)
    if t3 and t4 and t3["status"] == "SUCCESS" and t4["status"] == "SUCCESS":
        print(f"  Test 3 (safe entry): {t3['sif_probability']:.4f}")
        print(f"  Test 4 (dangerous entry): {t4['sif_probability']:.4f}")
        if t3["sif_status"] == "NO" and t4["sif_status"] == "YES":
            print(f"  ✓ PASS: Model correctly distinguishes safe vs dangerous confined space scenarios")
        else:
            print(f"  ❌ FAIL: Model should distinguish these scenarios differently")
    
    # Check 4: Test 5 vs Test 6 (safe vs dangerous height)
    print("\n4. TEST 5 (Safe Height) vs TEST 6 (Dangerous Height)")
    print("-" * 100)
    t5 = next((r for r in results if r["test_id"] == 5), None)
    t6 = next((r for r in results if r["test_id"] == 6), None)
    if t5 and t6 and t5["status"] == "SUCCESS" and t6["status"] == "SUCCESS":
        print(f"  Test 5 (safe work): {t5['sif_probability']:.4f}")
        print(f"  Test 6 (dangerous work): {t6['sif_probability']:.4f}")
        if t5["sif_status"] == "NO" and t6["sif_status"] == "YES":
            print(f"  ✓ PASS: Model correctly distinguishes safe vs dangerous height scenarios")
        else:
            print(f"  ❌ FAIL: Model should distinguish these scenarios differently")
    
    # Check 5: Test 7 vs Test 8 (safe vs dangerous lifting)
    print("\n5. TEST 7 (Safe Lifting) vs TEST 8 (Dangerous Lifting)")
    print("-" * 100)
    t7 = next((r for r in results if r["test_id"] == 7), None)
    t8 = next((r for r in results if r["test_id"] == 8), None)
    if t7 and t8 and t7["status"] == "SUCCESS" and t8["status"] == "SUCCESS":
        print(f"  Test 7 (safe lift): {t7['sif_probability']:.4f}")
        print(f"  Test 8 (dangerous lift): {t8['sif_probability']:.4f}")
        if t7["sif_status"] == "NO" and t8["sif_status"] == "YES":
            print(f"  ✓ PASS: Model correctly distinguishes safe vs dangerous lifting scenarios")
        else:
            print(f"  ❌ FAIL: Model should distinguish these scenarios differently")
    
    # Check 6: Test 9 (ambiguous)
    print("\n6. TEST 9 (Ambiguous/Insufficient Information)")
    print("-" * 100)
    t9 = next((r for r in results if r["test_id"] == 9), None)
    if t9 and t9["status"] == "SUCCESS":
        print(f"  Test 9 status: {t9['sif_status']}")
        print(f"  Test 9 probability: {t9['sif_probability']:.4f}")
        if t9["sif_status"] == "UNCERTAIN":
            print(f"  ✓ PASS: Model recognizes ambiguous case as UNCERTAIN")
        elif 0.45 < t9["sif_probability"] < 0.55:
            print(f"  ✓ PASS: Model recognizes ambiguous case (probability in uncertain range)")
        else:
            print(f"  ⚠ CONCERN: Model should recognize this as uncertain")
    
    # Check 7: Test 10 (keyword bias test - MOST IMPORTANT)
    print("\n7. TEST 10 (Keyword Bias - MOST IMPORTANT)")
    print("-" * 100)
    t10 = next((r for r in results if r["test_id"] == 10), None)
    if t10 and t10["status"] == "SUCCESS":
        print(f"  Test 10 status: {t10['sif_status']}")
        print(f"  Test 10 probability: {t10['sif_probability']:.4f}")
        if t10["sif_status"] == "NO":
            print(f"  ✓ PASS: Model understands CONTEXT and correctly ignores keyword bias")
            print(f"      (Report contains 'electrical', 'hazardous' but correctly classified as SAFE)")
        else:
            print(f"  ❌ FAIL: Model may be using keyword bias instead of semantic understanding")
    
    # Probability clustering analysis
    print("\n\n" + "="*100)
    print("PROBABILITY CLUSTERING ANALYSIS")
    print("="*100)
    
    if len(probabilities) >= 2:
        print(f"\nAll probabilities (n={len(probabilities)}): {[f'{p:.4f}' for p in probabilities]}")
        print(f"Min: {min(probabilities):.4f}")
        print(f"Max: {max(probabilities):.4f}")
        print(f"Mean: {mean(probabilities):.4f}")
        print(f"Std Dev: {stdev(probabilities):.4f}")
        print(f"Range: {max(probabilities) - min(probabilities):.4f}")
        
        # Check for clustering around 0.9
        high_cluster = [p for p in probabilities if p > 0.85]
        if len(high_cluster) >= len(probabilities) * 0.7:
            print(f"\n⚠ WARNING: {len(high_cluster)}/{len(probabilities)} probabilities clustered above 0.85")
            print(f"    This suggests potential probability calibration issue (like original 0.9 clustering)")
            print(f"    Detailed clustering: {[f'{p:.2f}' for p in sorted(probabilities)]}")
        else:
            print(f"\n✓ GOOD: Probabilities are well-distributed (not clustered)")
            print(f"    {len(high_cluster)} high-confidence, {len(probabilities)-len(high_cluster)} diverse")


def print_results_table(results):
    """Print a summary table of all results"""
    
    print("\n\n" + "="*100)
    print("RESULTS SUMMARY TABLE")
    print("="*100)
    print()
    
    print(f"{'#':<3} {'Test Name':<40} {'SIF':<12} {'Probability':<15} {'Confidence':<12} {'Risk':<12}")
    print("-" * 100)
    
    for r in results:
        if r["status"] == "SUCCESS":
            test_name = r["test_name"][:38]
            sif = r["sif_status"]
            prob = f"{r['sif_probability']:.4f}"
            conf = f"{r['confidence']}%"
            risk = r["risk_level"][:10]
            print(f"{r['test_id']:<3} {test_name:<40} {sif:<12} {prob:<15} {conf:<12} {risk:<12}")
        else:
            print(f"{r['test_id']:<3} {'ERROR':<40} {'N/A':<12} {'N/A':<15} {'N/A':<12} {'N/A':<12}")


def main():
    """Main test execution"""
    
    print("\nStarting test execution...")
    time.sleep(1)
    
    # Run tests
    results, probabilities = run_tests()
    
    # Print results table
    print_results_table(results)
    
    # Analyze for semantic differentiation
    analyze_results(results, probabilities)
    
    # Save results to file
    with open("d:/sif sentimental/10_case_sanity_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "test_cases": TEST_CASES,
            "results": results,
            "probabilities": probabilities
        }, f, indent=2, default=str)
    
    print("\n\nResults saved to: d:/sif sentimental/10_case_sanity_test_results.json")
    print("\n" + "="*100)
    print("TEST EXECUTION COMPLETE")
    print("="*100)


if __name__ == "__main__":
    main()
