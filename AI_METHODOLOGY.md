# SIF SENTINEL AI/NLP METHODOLOGY

## Overview

SIF Sentinel uses a **hybrid, deterministic-first approach** to NLP and SIF precursor detection. The system combines rule-based taxonomy matching with optional LLM enhancement and never relies on LLM results alone.

## Design Principles

1. **Transparency First** - Every detection decision includes explicit evidence
2. **Rule-Based Foundation** - Deterministic logic works when LLM is unavailable
3. **Conservative Detection** - Better to miss a precursor than falsely identify one
4. **No Fabrication** - Only report evidence actually present in the report
5. **Human-in-Loop** - All results require safety professional review

## Analysis Pipeline

### 1. Text Cleaning & Normalization

**Input**: Raw safety report text (unstructured, variable format)

**Process**:
- Convert to lowercase for case-insensitive matching
- Remove extra whitespace and special characters
- Preserve sentence structure and key punctuation

**Output**: Cleaned text ready for analysis

### 2. Evidence Extraction

**Purpose**: Identify key statements that support hazard detection

**Method**:
- Split text into sentences
- Filter sentences >= 10 characters
- Retain sentences containing SIF taxonomy keywords
- Limit to 5 most relevant evidence items

**Example**:
```
Input: "During maintenance, a worker entered an energized equipment 
area without completing the required isolation procedure."

Evidence:
- "entered an energized equipment area"
- "without completing the required isolation procedure"
```

### 3. Hazard Detection via Taxonomy Matching

**Taxonomy Structure**:
```
Categories:
├── HAZARDOUS_ENERGY (electrical, mechanical, hydraulic, pneumatic, LOTO)
├── WORKING_AT_HEIGHT (falls, unprotected edges, scaffolding)
├── LINE_OF_FIRE (struck by, caught between, suspended loads)
├── CONFINED_SPACE (unauthorized entry, atmospheric hazards)
├── VEHICLE_MOBILE_EQUIPMENT (pedestrian interaction, collision)
└── CRITICAL_CONTROL_FAILURE (permit, PPE, barrier, isolation failures)
```

**Matching Algorithm**:

For each category in taxonomy:
1. Get keyword list
2. For each keyword:
   - Use word boundary regex matching
   - Check if keyword appears in cleaned text
3. If any keyword matches, mark category as detected

**Keyword Examples**:
- LOTO failure: "energized", "high voltage", "without isolation", "without loto"
- Working at height: "height", "fall", "edge", "scaffold", "ladder", "roof"
- Confined space: "confined space", "gas monitoring", "oxygen", "entry"

### 4. Exposure Identification

**Purpose**: Determine type and magnitude of worker exposure

**Exposure Types**:
- **Direct Contact**: Worker touching hazard
- **Full Exposure**: Worker in hazard area
- **Partial Exposure**: Worker in partial hazard area
- **Proximity**: Worker nearby
- **Repeated Exposure**: Recurring hazard encounter

**Detection**:
- Match exposure keywords: "contact", "entered", "inside", "exposed", "near"
- If worker mentioned but no exposure type detected, infer "Proximity"

### 5. Control Failure Detection

**Purpose**: Identify where safety controls were inadequate

**Control Failure Types**:
- **LOTO/Isolation Failure**: Energy not isolated
- **Permit Failure**: Missing work permit/authorization
- **PPE Failure**: No protective equipment used
- **Barrier Bypass**: Removed or bypassed guards
- **Procedure Violation**: Procedures not followed
- **Lack of Monitoring**: Unattended/unsupervised work

**Detection**:
- Match control failure keywords
- Combine with hazard context
- Map to specific control type

### 6. SIF Status Determination

**Decision Logic**:

```
IF low_risk_keywords_found AND no_control_failures AND hazard_count <= 1
    → SIF_STATUS = NO
    → CONFIDENCE = 90%

ELIF no_hazards_detected
    → SIF_STATUS = NO
    → CONFIDENCE = 70%

ELIF no_exposure_detected
    → SIF_STATUS = UNCERTAIN
    → CONFIDENCE = 40%

ELIF critical_pattern_matched
    IF control_failures_detected
        → SIF_STATUS = YES
        → CONFIDENCE = 85%
    ELSE
        → SIF_STATUS = UNCERTAIN
        → CONFIDENCE = 70%

ELIF single_hazard_with_exposure
    IF control_failures_detected
        → SIF_STATUS = YES
        → CONFIDENCE = 75%
    ELSE
        → SIF_STATUS = UNCERTAIN
        → CONFIDENCE = 55%

ELIF multiple_hazards_with_exposure
    IF control_failures_detected
        → SIF_STATUS = YES
        → CONFIDENCE = 80%
    ELSE
        → SIF_STATUS = UNCERTAIN
        → CONFIDENCE = 65%

ELSE
    → SIF_STATUS = UNCERTAIN
    → CONFIDENCE = 50%
```

### 7. SIF Precursor Pattern Matching

**Patterns** are explicit multi-condition checks:

Example: `HAZARDOUS_ENERGY_LOTO`
```
Required conditions (ALL must match):
1. "energized" OR "high voltage" OR "live electrical"
2. "without isolation" OR "without loto" OR "lockout" OR "tagout"
3. "worker" OR "entered" OR "exposure"

When matched:
→ High confidence SIF precursor detected
→ Recommendation for LOTO procedure review
```

### 8. Risk Scoring

**Prototype Methodology** (for demonstration only):

```
Risk Score = 
    0.35 × Hazard_Severity +
    0.25 × Exposure_Severity +
    0.30 × Control_Failure_Severity +
    0.10 × Consequence_Potential

Risk Mapping:
    Score >= 80  → CRITICAL
    Score 60-79  → HIGH
    Score 40-59  → MEDIUM
    Score < 40   → LOW
```

**Component Scores**:
- Hazard severity: Category-specific (0.75-0.95 for critical hazards)
- Exposure severity: Exposure type-specific (0.50-1.0)
- Control failure severity: Failure type-specific (0.70-0.95)
- Consequence potential: Match injury-related keywords

### 9. Explanation Generation

**Purpose**: Provide transparent reasoning for AI decision

**Format**:
1. Overall status statement
2. Detected components (hazards, exposure, controls)
3. Key evidence from report
4. Confidence caveats

**Example**:
```
"Potential SIF precursor detected. The report describes exposure 
to hazardous energy (energized equipment) combined with critical 
control failure (LOTO isolation not completed). Evidence: 
'worker entered an energized equipment area without completing 
the required isolation procedure.'"
```

### 10. Recommendation Generation

**Source**: Recommendation engine maps hazards/controls to safety actions

**Process**:
1. Get recommendations for each detected hazard
2. Get recommendations for each control failure
3. Remove duplicates
4. Sort by priority (CRITICAL > HIGH > MEDIUM > LOW)
5. Generate priority action based on risk level

**Example Recommendations**:
- LOTO: "Verify all energy isolation procedures are properly followed"
- Fall Protection: "Review fall-protection controls and verify use"
- Confined Space: "Verify atmospheric testing and entry authorization"

## LLM Integration (Optional)

## Local ML Baseline

The application includes a reproducible supervised baseline in `backend/train_model.py`.
It trains a TF-IDF vectorizer with logistic regression on `data/training_reports.csv` and
saves the artifact to `backend/models/sif_model.joblib`. The current bootstrap dataset has
47 manually authored examples (22 NO, 25 YES), split into 35 training and 12 test records.
The recorded evaluation is 66.7% accuracy, 62.5% YES precision, 83.3% YES recall, and
71.4% YES F1. These are prototype measurements, not production or OIL-certified results.

The model's calibrated YES probability is returned as `sif_probability`. A probability of
at least 0.55 is classified as YES, at most 0.45 as NO, and values between them as
UNCERTAIN. The taxonomy layer remains responsible for hazard, control-failure, evidence,
and recommendation extraction. If the artifact is unavailable, the API explicitly falls
back to the deterministic rule engine and reports `RULE_ENGINE` as the model type.

Production training requires a substantially larger, expert-reviewed, versioned dataset
with independent labels and a held-out evaluation set.

**When LLM is configured**:
1. Rule engine produces initial analysis (always)
2. LLM validates and enriches results (if configured)
3. LLM is instructed:
   - Only use evidence from provided report
   - Never invent information
   - Return UNCERTAIN if evidence insufficient
   - Defer to rule engine on ambiguous cases
   - Never claim to predict outcomes

**LLM Prompt Structure**:
```
You are a workplace safety expert. Analyze this safety report 
for SIF precursor patterns using this taxonomy: [taxonomy].

Report: [report_text]

Return structured JSON with:
- sif_status (YES/NO/UNCERTAIN)
- confidence (0-100)
- hazards (list)
- control_failures (list)
- explanation (evidence-based only)

CRITICAL: Only report what is explicitly stated in the report.
Do not invent or assume information.
```

## Model Versioning

**Current Model**: v1.0
- Deterministic rule-based
- 6 hazard categories
- 5 SIF precursor patterns
- No LLM dependency

**Future**:
- v1.1: LLM optional enhancement
- v2.0: Trained on verified safety data (if available)
- v3.0: Feedback-based improvement loop

## Accuracy & Limitations

**Important Notes**:

1. **No Ground Truth**: This prototype lacks verified SIF precursor labels
2. **OSHA Data Mismatch**: OSHA data has injury outcomes, not precursor labels
3. **Synthetic Labels**: Synthetic data uses rule-based labels, not expert judgment
4. **Conservative Bias**: System may over-report to avoid missing real risks
5. **Context Loss**: Unstructured text loses operational context
6. **Methodology Validation**: Prototype approach not scientifically validated

**Expected Behavior**:
- High false positive rate (intentional - safety first)
- Misses rare precursor combinations
- Sensitive to report writing style
- Requires human safety professional review

## Transparency & Explainability

Every analysis includes:
- ✓ Exact evidence from report
- ✓ Explanation of detection logic
- ✓ Confidence level
- ✓ Model and version info
- ✓ Required human review statement
- ✓ Control failure identification
- ✓ Specific recommendations

## Testing & Validation

**Test Cases** (in tests/ directory):

- Keyword matching accuracy
- Hazard detection coverage
- Exposure classification
- Control failure identification
- Risk score calculation
- Recommendation generation
- CSV parsing
- API health checks

**Example Test Report**:
```
"During maintenance, a worker entered an energized equipment area 
without completing the required isolation procedure."

Expected:
- Hazard: HAZARDOUS_ENERGY
- Exposure: Full Exposure
- Control Failure: LOTO/Isolation Failure
- SIF Status: YES
- Risk: CRITICAL / HIGH
```

## Compliance & Safety

This methodology is designed for:
- **Hackathon Prototype**: Proof of concept
- **Decision Support**: Not replacement for expert review
- **Prioritization**: Flagging reports for human expert attention
- **Learning**: Understanding SIF precursor patterns

**Not Designed For**:
- ❌ Standalone safety decisions
- ❌ Regulatory compliance determination
- ❌ Outcome prediction
- ❌ Production deployment without validation

## References & Future Improvements

**Potential Enhancements**:
- Integration with OIL historical safety data
- Domain-specific model fine-tuning
- Multilingual support
- Voice report analysis
- Real-time learning from human validations
- Advanced NLP techniques (BERT, transformer models)
- Causal inference for control effectiveness

**For Production Deployment**:
1. Collect verified SIF precursor labels (1000+ examples)
2. Domain expert validation of taxonomy
3. Compare with official OIL methodology
4. Establish human validation baselines
5. Implement feedback-based model improvement
6. Rigorous testing and validation
7. Regulatory review and approval
8. Ongoing monitoring and updates

---

**Version**: 1.0
**Last Updated**: 2024-01-01
**For**: Smart India Hackathon 2026 - SIH26165
