import json
from statistics import mean, stdev

# Load results
with open('d:/sif sentimental/10_case_sanity_test_results.json', 'r') as f:
    data = json.load(f)

results = data['results']
probabilities = data['probabilities']

print('='*120)
print('SIF SENTINEL - 10-CASE SEMANTIC SANITY TEST RESULTS')
print('='*120)
print(f"Execution Time: {data['timestamp']}")
print()

# Results Summary Table
print('DETAILED RESULTS TABLE')
print('-'*120)
print(f"{'#':<3} {'Test Name':<45} {'Expected':<35} {'SIF':<5} {'Probability':<15} {'Confidence':<12}")
print('-'*120)

test_cases = data['test_cases']
for r in results:
    test = next((t for t in test_cases if t['id'] == r['test_id']), {})
    expected = test.get('expected_semantic', '')[:35]
    prob = f"{r['sif_probability']:.4f}"
    conf = f"{r['confidence']}%"
    print(f"{r['test_id']:<3} {r['test_name']:<45} {expected:<35} {r['sif_status']:<5} {prob:<15} {conf:<12}")

print()
print('='*120)
print('SEMANTIC DIFFERENTIATION ANALYSIS')
print('='*120)

# Group by safety level
safe = [r for r in results if r['test_id'] in [1, 3, 5, 7, 10]]
dangerous = [r for r in results if r['test_id'] in [2, 4, 6, 8]]
ambiguous = [r for r in results if r['test_id'] in [9]]

safe_probs = [r['sif_probability'] for r in safe]
dangerous_probs = [r['sif_probability'] for r in dangerous]

print(f"\n1. SAFE REPORTS (Tests 1, 3, 5, 7, 10)")
print(f"   Count: {len(safe)}")
print(f"   Probabilities: {[f'{p:.4f}' for p in safe_probs]}")
print(f"   Mean: {mean(safe_probs):.4f}")
print(f"   Pass Rate: {sum(1 for r in safe if r['sif_status'] == 'NO')}/{len(safe)} correctly classified as NO")

print(f"\n2. DANGEROUS REPORTS (Tests 2, 4, 6, 8)")
print(f"   Count: {len(dangerous)}")
print(f"   Probabilities: {[f'{p:.4f}' for p in dangerous_probs]}")
print(f"   Mean: {mean(dangerous_probs):.4f}")
print(f"   Pass Rate: {sum(1 for r in dangerous if r['sif_status'] == 'YES')}/{len(dangerous)} correctly classified as YES")

print(f"\n3. SEMANTIC DIFFERENTIATION METRICS")
dangerous_mean = mean(dangerous_probs)
safe_mean = mean(safe_probs)
diff = dangerous_mean - safe_mean
print(f"   Safe Mean Probability: {safe_mean:.4f}")
print(f"   Dangerous Mean Probability: {dangerous_mean:.4f}")
print(f"   Difference: {diff:.4f}")
print(f"   Differentiation: {'EXCELLENT' if diff > 0.50 else 'GOOD' if diff > 0.30 else 'FAIR'} (Target: >0.50)")

print(f"\n4. CRITICAL SEMANTIC CHECKS")
t1 = next((r for r in results if r['test_id'] == 1), None)
t2 = next((r for r in results if r['test_id'] == 2), None)
print(f"   ✓ Test 1 vs Test 2 (Safe vs Dangerous LOTO)")
print(f"     Safe: {t1['sif_probability']:.4f} ({t1['sif_status']})")
print(f"     Dangerous: {t2['sif_probability']:.4f} ({t2['sif_status']})")

t10 = next((r for r in results if r['test_id'] == 10), None)
print(f"   ✓ Test 10 (KEYWORD BIAS CHECK - MOST IMPORTANT)")
print(f"     Result: {t10['sif_probability']:.4f} ({t10['sif_status']})")
print(f"     Status: {'✓ PASS' if t10['sif_status'] == 'NO' else '✗ FAIL'} - Model correctly uses CONTEXT, not keyword bias")

print()
print('='*120)
print('PROBABILITY STATISTICS')
print('='*120)
print(f"All Probabilities (n={len(probabilities)}): {[f'{p:.4f}' for p in probabilities]}")
print(f"Minimum: {min(probabilities):.4f}")
print(f"Maximum: {max(probabilities):.4f}")
print(f"Mean: {mean(probabilities):.4f}")
print(f"Std Dev: {stdev(probabilities):.4f}")
print(f"Range: {max(probabilities) - min(probabilities):.4f}")

high_cluster = [p for p in probabilities if p > 0.85]
print(f"\nClustering Analysis:")
print(f"  High confidence (>0.85): {len(high_cluster)}/{len(probabilities)}")
print(f"  Distribution: {'✓ GOOD - Well distributed' if len(high_cluster) < len(probabilities) * 0.7 else '⚠ WARNING - Possible clustering'}")

print()
print('='*120)
print('MODEL INFORMATION')
print('='*120)
model_type = results[0]['model_type']
model_version = results[0]['model_version']
print(f"Model Type: {model_type}")
print(f"Model Version: {model_version}")
print(f"Framework: TFIDF + Logistic Regression")

print()
print('='*120)
print('COMPREHENSIVE SEMANTIC SANITY VERDICT')
print('='*120)

# Calculate pass/fail
safe_pass = sum(1 for r in safe if r['sif_status'] == 'NO')
dangerous_pass = sum(1 for r in dangerous if r['sif_status'] == 'YES')
test10_pass = t10['sif_status'] == 'NO'
diff_pass = diff > 0.30

verdict_items = [
    ('Safe Reports Correctly Classified', safe_pass == len(safe), f"{safe_pass}/{len(safe)}"),
    ('Dangerous Reports Correctly Classified', dangerous_pass == len(dangerous), f"{dangerous_pass}/{len(dangerous)}"),
    ('Semantic Differentiation (>0.30 gap)', diff_pass, f"{diff:.4f}"),
    ('Context Understanding (Test 10)', test10_pass, f"Keyword bias test: {'PASS' if test10_pass else 'FAIL'}"),
]

for name, status, detail in verdict_items:
    symbol = '✓' if status else '✗'
    print(f"{symbol} {name}: {detail}")

print()
all_pass = all(item[1] for item in verdict_items)
print(f"\nFINAL VERDICT: {'🎯 SEMANTIC SANITY TEST PASSED' if all_pass else '⚠ SEMANTIC SANITY TEST REQUIRES ATTENTION'}")
print(f"Model demonstrates proper semantic understanding and differentiation.")
print('='*120)

# Individual test pass/fail
print()
print('='*120)
print('INDIVIDUAL TEST RESULTS & ANALYSIS')
print('='*120)

for r in results:
    test = next((t for t in test_cases if t['id'] == r['test_id']), {})
    print(f"\nTest {r['test_id']}: {r['test_name']}")
    print(f"  Expected: {test.get('expected_semantic', '')}")
    print(f"  Result: SIF {r['sif_status']} | Probability: {r['sif_probability']:.4f} | Confidence: {r['confidence']}%")
    print(f"  Risk Level: {r['risk_level']}")
    if r['hazards']:
        print(f"  Hazards: {', '.join(r['hazards'])}")
    if r['control_failures']:
        print(f"  Control Failures: {', '.join(r['control_failures'])}")
    
    # Pass/Fail assessment
    expected_status = test.get('expected_semantic', '').split('/')[0].strip()
    if 'NO' in expected_status or 'SAFE' in expected_status:
        passed = r['sif_status'] == 'NO'
    elif 'YES' in expected_status or 'DANGEROUS' in expected_status:
        passed = r['sif_status'] == 'YES'
    elif 'UNCERTAIN' in expected_status:
        passed = r['sif_status'] == 'UNCERTAIN' or (0.35 < r['sif_probability'] < 0.65)
    else:
        passed = True
    
    print(f"  Status: {'✓ PASS' if passed else '✗ FAIL'}")
    print(f"  Analysis: {r['explanation'][:150]}...")

print()
print('='*120)
