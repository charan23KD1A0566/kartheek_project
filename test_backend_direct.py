#!/usr/bin/env python3
"""
Direct test of the SIF Sentinel backend API
Test the 10 semantic cases directly
"""

import requests
import json
import time
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
        "expected": "SAFE / NO SIF"
    },
    {
        "id": 2,
        "name": "DANGEROUS ELECTRICAL EXPOSURE",
        "text": "Worker entered an energized electrical area without completing lockout and isolation. The equipment remained energized while maintenance was being performed.",
        "expected": "DANGEROUS / SIF YES"
    },
    {
        "id": 3,
        "name": "SAFE CONFINED SPACE PREPARATION",
        "text": "The confined-space entry permit was approved before work. Atmospheric testing was completed, ventilation was established, and the rescue plan and trained attendant were confirmed.",
        "expected": "SAFE / NO SIF"
    },
    {
        "id": 4,
        "name": "DANGEROUS CONFINED SPACE ENTRY",
        "text": "Worker entered a confined space without atmospheric testing or an approved permit. No trained attendant or rescue arrangement was available.",
        "expected": "DANGEROUS / SIF YES"
    },
    {
        "id": 5,
        "name": "SAFE WORKING AT HEIGHT",
        "text": "Worker performed roof maintenance using inspected scaffolding, complete guardrails and an approved fall-arrest harness. The equipment was inspected before use.",
        "expected": "SAFE / NO SIF"
    },
    {
        "id": 6,
        "name": "FALL PROTECTION FAILURE",
        "text": "Worker performed roof work near an unprotected edge without a harness, guardrail or other fall protection system.",
        "expected": "DANGEROUS / SIF YES"
    },
    {
        "id": 7,
        "name": "SAFE LIFTING OPERATION",
        "text": "The lifting zone was barricaded and access was restricted. The crane was inspected and the load was secured before lifting. No person was permitted beneath the suspended load.",
        "expected": "SAFE / NO SIF"
    },
    {
        "id": 8,
        "name": "LINE-OF-FIRE EXPOSURE",
        "text": "A suspended load moved over an occupied work area while a worker remained directly underneath it. No exclusion zone or barricade was established.",
        "expected": "DANGEROUS / SIF YES"
    },
    {
        "id": 9,
        "name": "AMBIGUOUS / INSUFFICIENT INFORMATION",
        "text": "Electrical maintenance activity was observed in the work area. The report does not state whether the equipment was isolated or whether the worker was exposed to hazardous energy.",
        "expected": "UNCERTAIN"
    },
    {
        "id": 10,
        "name": "SAFE REPORT WITH DANGEROUS-SOUNDING KEYWORDS",
        "text": "Worker used PPE while performing routine electrical maintenance. The equipment was isolated before work, the permit was verified, all safeguards were checked, and no hazardous exposure occurred.",
        "expected": "SAFE / NO SIF"
    }
]


def get_auth_token():
    """Authenticate and get access token"""
    try:
        print("Attempting authentication...")
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json={"email": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Authentication failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
        
        data = response.json()
        token = data.get("access_token")
        if token:
            print(f"Successfully authenticated")
            return token
        else:
            print("No access token in response")
            return None
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return None


def run_tests():
    """Execute all 10 test cases"""
    
    print("=" * 100)
    print("FINAL 10-CASE AI SANITY TEST")
    print("=" * 100)
    print()
    
    # Authenticate first
    print("Step 1: Authenticating with backend...")
    token = get_auth_token()
    if not token:
        print("FAILED: Cannot authenticate")
        return []
    
    print()
    print("=" * 100)
    print("Step 2: Running semantic tests...")
    print("=" * 100)
    print()
    
    results = []
    probabilities = []
    
    for test in TEST_CASES:
        print(f"\nTEST {test['id']}: {test['name']}")
        print(f"Expected: {test['expected']}")
        print(f"Text: {test['text'][:80]}...")
        
        try:
            response = requests.post(
                f"{API_URL}/api/analyze",
                json={"text": test["text"]},
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"ERROR: HTTP {response.status_code}")
                print(f"Response: {response.text[:200]}")
                results.append({
                    "test_id": test["id"],
                    "test_name": test["name"],
                    "status": "ERROR",
                    "error": f"HTTP {response.status_code}"
                })
                continue
            
            data = response.json()
            
            sif_status = data.get("sif_status", "UNKNOWN")
            sif_probability = float(data.get("sif_probability", 0.0))
            confidence = data.get("confidence", 0)
            risk_level = data.get("risk_level", "UNKNOWN")
            model_type = data.get("model_type", "UNKNOWN")
            
            probabilities.append(sif_probability)
            
            print(f"RESULT: {sif_status} | Probability: {sif_probability:.4f} | Confidence: {confidence}% | Risk: {risk_level} | Model: {model_type}")
            
            results.append({
                "test_id": test["id"],
                "test_name": test["name"],
                "expected": test["expected"],
                "sif_status": sif_status,
                "sif_probability": sif_probability,
                "confidence": confidence,
                "risk_level": risk_level,
                "model_type": model_type,
                "status": "SUCCESS"
            })
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append({
                "test_id": test["id"],
                "test_name": test["name"],
                "status": "ERROR",
                "error": str(e)
            })
        
        time.sleep(0.3)
    
    return results, probabilities


def main():
    try:
        results, probabilities = run_tests()
        
        print("\n\n" + "=" * 100)
        print("RESULTS SUMMARY")
        print("=" * 100)
        
        # Print results table
        print("\nTest Results:")
        print(f"{'#':<3} {'Name':<40} {'Expected':<20} {'Result':<20} {'Probability':<15} {'Status':<10}")
        print("-" * 110)
        
        for r in results:
            if r["status"] == "SUCCESS":
                prob = f"{r['sif_probability']:.4f}"
                print(f"{r['test_id']:<3} {r['test_name']:<40} {r['expected']:<20} {r['sif_status']:<20} {prob:<15} {r['status']:<10}")
            else:
                print(f"{r['test_id']:<3} {r['test_name']:<40} {r['expected']:<20} {'ERROR':<20} {'N/A':<15} {r['status']:<10}")
        
        # Probability analysis
        if probabilities:
            print("\n\n" + "=" * 100)
            print("PROBABILITY STATISTICS")
            print("=" * 100)
            print(f"Min probability: {min(probabilities):.4f}")
            print(f"Max probability: {max(probabilities):.4f}")
            print(f"Mean probability: {mean(probabilities):.4f}")
            if len(probabilities) > 1:
                print(f"Std Dev: {stdev(probabilities):.4f}")
            
            # Group by semantic type
            safe_tests = [r for r in results if r["test_id"] in [1, 3, 5, 7, 10] and r["status"] == "SUCCESS"]
            dangerous_tests = [r for r in results if r["test_id"] in [2, 4, 6, 8] and r["status"] == "SUCCESS"]
            
            if safe_tests:
                safe_probs = [r["sif_probability"] for r in safe_tests]
                print(f"\nSafe reports (Tests 1,3,5,7,10):")
                print(f"  Mean probability: {mean(safe_probs):.4f}")
                for r in safe_tests:
                    print(f"    Test {r['test_id']}: {r['sif_probability']:.4f}")
            
            if dangerous_tests:
                dangerous_probs = [r["sif_probability"] for r in dangerous_tests]
                print(f"\nDangerous reports (Tests 2,4,6,8):")
                print(f"  Mean probability: {mean(dangerous_probs):.4f}")
                for r in dangerous_tests:
                    print(f"    Test {r['test_id']}: {r['sif_probability']:.4f}")
            
            if safe_tests and dangerous_tests:
                diff = mean(dangerous_probs) - mean(safe_probs)
                print(f"\nDifferentiation: Dangerous mean - Safe mean = {diff:.4f}")
                if diff > 0.15:
                    print("Status: GOOD DIFFERENTIATION")
                elif diff > 0.05:
                    print("Status: MODERATE DIFFERENTIATION")
                else:
                    print("Status: POOR DIFFERENTIATION - Model may not be learning properly")
        
        # Save results to file
        with open("d:\\sif sentimental\\10_case_sanity_test_results.json", "w") as f:
            json.dump({
                "timestamp": str(time.time()),
                "results": results,
                "summary": {
                    "total_tests": len(results),
                    "successful": len([r for r in results if r["status"] == "SUCCESS"]),
                    "failed": len([r for r in results if r["status"] == "ERROR"]),
                    "probabilities": {
                        "min": min(probabilities) if probabilities else None,
                        "max": max(probabilities) if probabilities else None,
                        "mean": mean(probabilities) if probabilities else None,
                        "stdev": stdev(probabilities) if len(probabilities) > 1 else None
                    }
                }
            }, f, indent=2)
        
        print("\n\nResults saved to: d:\\sif sentimental\\10_case_sanity_test_results.json")
        
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
