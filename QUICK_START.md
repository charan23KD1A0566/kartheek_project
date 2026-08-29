# SIF Sentinel - Quick Start & Testing Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+ with npm
- MongoDB running locally on port 27017
- Windows PowerShell or terminal

### Backend Setup & Start

```powershell
cd "d:\sif sentimental\backend"

# Verify model is present
dir models\
# Should show: sif_model.joblib, model_metadata.json

# Start backend server
python -m uvicorn main:app --reload --port 8000
```

Backend will start on http://localhost:8000

### Frontend Setup & Start

```powershell
cd "d:\sif sentimental\frontend"

# Install dependencies (if needed)
npm install

# Start development server
npm run dev
```

Frontend will start on http://localhost:5173

### Test in Browser

1. **Login**
   - URL: http://localhost:5173
   - Employee credentials: (see section below)
   - Manager credentials: (see section below)

2. **Submit a Report** (as Employee)
   - Click "New Report"
   - Enter report text
   - Submit
   - See AI analysis results immediately

3. **Review Reports** (as Manager)
   - Login as manager
   - Go to Reports
   - See list of all reports with SIF status
   - Click to view detailed analysis
   - Check for high-risk alerts

---

## 🧪 Testing the AI Model

### Test 1: Model Prediction Diversity
Verify the model produces diverse predictions (not 0.9 for everything):

```powershell
cd "d:\sif sentimental\backend"
python test_model_predictions.py
```

Expected output:
```
✓ Safe reports mostly NO (6/6)
✓ Dangerous reports mostly YES (7/7)
✓ YES probabilities diverse (range=0.980)
✓ Model distinguishes similar scenarios
VALIDATION RESULT: 5/5 checks passed ✅
```

### Test 2: API End-to-End Pipeline
Verify the complete analysis pipeline works:

```powershell
cd "d:\sif sentimental\backend"
python test_api_integration.py
```

Expected output:
```
✓ AI Engine initialized
✓ Model loaded: True
✓ All API components working correctly
```

### Test 3: Backend Compilation
Verify Python code has no syntax errors:

```powershell
cd "d:\sif sentimental\backend"
python -m compileall -q .
echo "Backend OK!"
```

### Test 4: Model Loading
Verify the trained model loads correctly:

```powershell
cd "d:\sif sentimental\backend"
python -c "import joblib; m = joblib.load('models\sif_model.joblib'); print('Model loaded:', type(m).__name__); print('Classes:', m.classes_)"
```

### Test 5: Frontend Build
Verify frontend builds successfully:

```powershell
cd "d:\sif sentimental\frontend"
npm run build
# Should end with: ✓ built in X.XXs
# EXIT_CODE should be 0
```

---

## 📊 Test Sample Reports

Use these reports to manually test the AI model:

### SAFE Report (Should predict NO)
```
The electrical panel was isolated and locked out. Zero energy was verified 
before maintenance began. Worker wore required PPE throughout the task.
```
Expected: SIF Status = NO, Probability = ~0-10%

### DANGEROUS Report (Should predict YES)
```
Worker entered the energized electrical panel without completing lockout 
and isolation procedures. No isolation verification was performed.
```
Expected: SIF Status = YES, Probability = ~90-99%

### AMBIGUOUS Report (Should predict UNCERTAIN or moderate probability)
```
Electrical maintenance was performed. The exact conditions and control measures 
are not fully documented in the report.
```
Expected: SIF Status = UNCERTAIN or NO, Probability = 30-50%

### TRICKY Report - Safe despite dangerous words
```
PPE was properly worn to prevent chemical exposure. The confined space was 
well-ventilated, tested, and a safety officer was stationed.
```
Expected: SIF Status = NO, Probability = ~0-10%

---

## 📁 Key File Locations

### Model & Training Data
- `d:\sif sentimental\backend\models\sif_model.joblib` - Trained ML model
- `d:\sif sentimental\backend\models\model_metadata.json` - Model metrics
- `d:\sif sentimental\data\training_reports.csv` - Training dataset (771 records)
- `d:\sif sentimental\data\model_test_results.csv` - Test results

### Backend
- `d:\sif sentimental\backend\main.py` - FastAPI application
- `d:\sif sentimental\backend\services\ai_engine.py` - AI analysis pipeline
- `d:\sif sentimental\backend\database.py` - MongoDB setup
- `d:\sif sentimental\backend\train_model.py` - Model training script

### Frontend
- `d:\sif sentimental\frontend\src\App.jsx` - Main app with routing
- `d:\sif sentimental\frontend\src\pages\NewReportPage.jsx` - Report submission
- `d:\sif sentimental\frontend\src\pages\ReportDetailPage.jsx` - Analysis display

### Documentation
- `d:\sif sentimental\FINAL_REPORT.md` - Complete project report
- `d:\sif sentimental\README.md` - Project overview
- `d:\sif sentimental\ARCHITECTURE.md` - System architecture

---

## 🔧 Model Details

### Model Specification
- **Type**: TF-IDF + Logistic Regression + Sigmoid Calibration
- **File**: `sif_model.joblib` (CalibratedClassifierCV)
- **Version**: 2.0 (Calibrated)
- **Training Data**: 771 records
- **Test Accuracy**: 93.55%

### Classes
- `YES` - Serious Injury/Fatality precursor detected
- `NO` - No SIF precursor
- `UNCERTAIN` - Insufficient information

### Thresholds
- SIF Probability ≥ 0.55 → Predict YES
- SIF Probability ≤ 0.45 → Predict NO
- 0.45 < Probability < 0.55 → Predict UNCERTAIN

### Probability Calibration
- Used: Sigmoid calibration (Platt scaling)
- Purpose: Make probabilities reflect true model confidence
- Result: Probabilities range 0.34-0.99 (not clustered at 0.9)

---

## 👥 Test User Accounts

### Employee Account
- Email: employee@sif.local
- Password: test123
- Role: employee
- Permissions: Submit reports, view own reports

### Manager Account
- Email: manager@sif.local
- Password: test123
- Role: manager
- Permissions: View all reports, receive alerts, validate reports

### Safety Officer Account
- Email: safety@sif.local
- Password: test123
- Role: safety_officer
- Permissions: View all reports, receive alerts, validate reports

### Admin Account
- Email: admin@sif.local
- Password: test123
- Role: admin
- Permissions: Full system access

**Note**: First-time login may require account creation in MongoDB. Check the backend 
logs for seed_demo_data() output to confirm accounts exist.

---

## ⚠️ Alert System Testing

### Trigger an Alert
1. Login as Employee
2. Submit a report with dangerous keywords:
   ```
   Worker attempted to service energized electrical panel without 
   completing lockout and isolation procedures.
   ```
3. System will create alert with SIF=YES, RISK=CRITICAL
4. Login as Manager
5. Check alerts inbox
6. Alert should appear

---

## 🐛 Troubleshooting

### Backend won't start
- Check: Is MongoDB running? (`mongosh` should connect)
- Check: Is port 8000 already in use? (Change in uvicorn command)
- Check: Are dependencies installed? (`pip install -r requirements.txt`)

### Model doesn't load
- Check: Does `models/sif_model.joblib` exist?
- Check: Is joblib installed? (`pip install joblib`)
- Check: Run `python test_api_integration.py` for diagnostics

### Frontend won't build
- Check: Is Node.js installed? (`node --version`)
- Check: Are dependencies installed? (`npm install`)
- Check: Run `npm run build` to see detailed errors

### Analysis not showing
- Check: Is backend API responding? (Test http://localhost:8000/docs)
- Check: Is frontend configured for correct API URL? (Check `src/services/api.js`)
- Check: Check browser console for API errors

### No results in Reports page
- Check: Are reports saved to MongoDB?
- Check: Is employee account properly configured?
- Check: Check MongoDB with: `mongosh sif_sentinel`

---

## 📈 Model Performance Summary

| Metric | Value |
|--------|-------|
| Overall Accuracy | 93.55% |
| YES Precision | 93.27% |
| YES Recall | 97.0% |
| YES F1-Score | 0.951 |
| NO Precision | 92.11% |
| NO Recall | 83.33% |
| NO F1-Score | 0.875 |
| UNCERTAIN F1-Score | 1.0 |
| Probability Range | 0.34 - 0.99 |
| Calibration Method | Sigmoid |

---

## 🎯 Verification Checklist

Before going to production:

- [ ] Backend starts without errors
- [ ] Frontend builds with EXIT_CODE=0
- [ ] Model test passes (5/5 checks)
- [ ] API test passes (3/3 scenarios)
- [ ] Can login with test accounts
- [ ] Can submit report and see analysis
- [ ] Can view previous reports
- [ ] Alerts trigger for high-risk reports
- [ ] Responsive design works on 390px width
- [ ] MongoDB data persists

---

## 📝 Important Notes

1. **This is a PROTOTYPE** - Not production-ready for safety-critical decisions
2. **Manual Review Required** - All SIF predictions must be reviewed by qualified professionals
3. **Synthetic Training Data** - Model trained on generated examples, not real expert labels
4. **Limited Hazard Categories** - 11 hazard categories in current taxonomy
5. **No Email Alerts** - Currently in-app notifications only

---

## 🔗 API Reference

### Analyze a Report
```
POST /api/analyze
Content-Type: application/json
Authorization: Bearer {token}

{
  "text": "Worker wore required PPE and verified isolation before maintenance."
}

Response:
{
  "sif_status": "NO",
  "sif_probability": 0.0061,
  "confidence": 99,
  "risk_level": "LOW",
  "hazards": [],
  "control_failures": [],
  "evidence": ["worker wore required ppe"],
  "explanation": "...",
  "recommendation": "...",
  "safety_action_plan": {...},
  "model_type": "TFIDF_LOGISTIC",
  "model_version": "2.0"
}
```

### Create & Analyze Report
```
POST /api/reports
Content-Type: application/json
Authorization: Bearer {token}

{
  "report_text": "...",
  "report_type": "near_miss",
  "location": "Workshop A",
  "department": "Maintenance",
  "activity": "Equipment inspection",
  "date": "2026-08-29T00:00:00Z"
}

Response includes analysis result (same as /api/analyze)
```

---

**Last Updated**: August 29, 2026
**Model Version**: 2.0
**Status**: Ready for Testing ✅
