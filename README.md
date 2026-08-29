# SIF SENTINEL

**"Turning Safety Reports into Proactive SIF Intelligence"**

## Project Overview

SIF Sentinel is a decision-support system for detecting Serious Injury & Fatality (SIF) precursors in workplace safety reports. Built for the Smart India Hackathon 2026 (Problem Statement: SIH26165).

The system converts unstructured workplace safety reports into structured safety intelligence using hybrid AI/NLP analysis and a predefined SIF taxonomy.

## Important Disclaimer

⚠️ **This is a HACKATHON PROTOTYPE and decision-support system.**

- **Data Source**: Public OSHA data — NOT OIL operational data
- **AI Results**: Require human safety-professional review
- **No Predictive Claims**: System identifies potential SIF precursor patterns, does not predict outcomes
- **Decision Support**: Prioritizes reports for safety-professional review; never replaces human judgment

## Technology Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- Recharts (dashboards)
- Lucide React (icons)

### Backend
- Python 3.10+
- FastAPI
- Pydantic
- Uvicorn

### Database
- MongoDB
- PyMongo / Motor

### AI/NLP
- Deterministic taxonomy/rule engine
- LLM integration (OpenAI/similar) — optional, with fallback
- Python NLP preprocessing

## Project Structure

```
sif-sentinel/
├── frontend/                    # React + Vite application
│   ├── src/
│   │   ├── components/         # Reusable React components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API client services
│   │   ├── hooks/              # Custom React hooks
│   │   ├── utils/              # Utility functions
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── backend/                     # FastAPI application
│   ├── main.py                 # Entry point
│   ├── config.py               # Configuration
│   ├── database.py             # MongoDB connection
│   ├── models/                 # Pydantic models
│   ├── routes/                 # API endpoints
│   ├── services/               # Business logic
│   │   ├── ai_engine.py       # AI/NLP pipeline
│   │   ├── taxonomy.py        # SIF taxonomy
│   │   ├── risk_engine.py     # Risk scoring
│   │   └── recommendation_engine.py
│   ├── utils/                  # Utilities
│   ├── requirements.txt
│   └── .env.example
│
├── data/
│   ├── synthetic_reports.json  # 100+ synthetic reports
│   └── taxonomy.json           # SIF taxonomy configuration
│
├── scripts/
│   ├── seed_database.py        # Database initialization
│   └── ingest_osha.py          # OSHA CSV ingestion
│
├── tests/                       # Unit and integration tests
│
├── .env.example                # Environment template
├── .gitignore
├── docker-compose.yml          # MongoDB container config
├── README.md                   # This file
├── ARCHITECTURE.md             # Architecture documentation
├── AI_METHODOLOGY.md           # AI/NLP methodology
├── DATASET.md                  # Data source methodology
├── LIMITATIONS.md              # Known limitations
└── DEMO.md                     # Demo workflow

```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (via Docker or local installation)
- Git

### Installation

1. **Clone and Navigate**
```bash
cd sif-sentinel
```

2. **Setup Backend**
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

3. **Setup Frontend**
```bash
cd frontend
npm install
```

4. **Setup MongoDB**
```bash
# Using Docker:
docker-compose up -d

# Or install MongoDB locally and ensure it's running on mongodb://localhost:27017
```

5. **Initialize Database**
```bash
cd backend
python scripts/seed_database.py
```

### Running the Application

**Terminal 1 - Backend**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend**
```bash
cd frontend
npm run dev
```

Access: http://localhost:5173

## Demo Credentials

```
Admin User:
  Email: admin@sifsentinel.demo
  Password: Admin@123

Safety Officer:
  Email: safety@sifsentinel.demo
  Password: Safety@123

Manager:
  Email: manager@sifsentinel.demo
  Password: Manager@123
```

⚠️ These are DEMO credentials for prototype development only.

## Demo Workflow

1. **Login** with demo credentials
2. **Dashboard** - View KPIs and charts
3. **AI Analysis** - Paste the demo report:
   ```
   "During maintenance, a worker entered an energized equipment area 
   without completing the required isolation procedure."
   ```
4. **Analyze** - See SIF precursor detection
5. **Review Results** - Hazards, exposure, control failures, explanation
6. **Confirm** - Store validation
7. **Reports** - View stored analysis
8. **Analytics** - Track trends

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User authentication |
| POST | `/api/analyze` | Analyze a safety report |
| POST | `/api/reports` | Create report |
| GET | `/api/reports` | List reports |
| GET | `/api/reports/{id}` | Get report details |
| POST | `/api/reports/{id}/validate` | Human validation |
| POST | `/api/reports/upload` | CSV batch upload |
| GET | `/api/dashboard` | Dashboard statistics |
| GET | `/api/analytics` | Analytics data |
| GET | `/api/taxonomy` | Get SIF taxonomy |
| GET | `/api/health` | Health check |

## Key Features

### SIF Precursor Analysis
- Hybrid NLP (rule-based + optional LLM)
- Structured hazard detection
- Worker exposure assessment
- Critical control failure identification
- Evidence extraction
- AI explainability

### Risk Engine
- Transparent prototype scoring
- Documented methodology
- Configurable weights
- Risk levels: LOW / MEDIUM / HIGH / CRITICAL

### Human Validation
- AI-human agreement tracking
- Reviewer comments
- Audit logging

### Dashboard
- Real-time KPIs
- Risk distribution charts
- Hazard analytics
- Validation metrics

### Reporting
- Advanced search and filters
- Pagination
- Data source tracking
- Audit trails

### CSV Ingestion
- OSHA dataset support
- Column mapping
- Sample analysis
- Batch processing

## Environment Variables

```
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=sif_sentinel

# LLM Configuration (optional)
LLM_PROVIDER=openai          # or: anthropic, huggingface, etc.
LLM_API_KEY=sk_xxxx
LLM_MODEL=gpt-4

# Frontend API
FRONTEND_API_URL=http://localhost:8000/api

# Security
JWT_SECRET=your_secret_key_here
```

## Architecture

```
User
  ↓
React Frontend (Vite)
  ↓
FastAPI Backend
  ↓
  ├─ AI/NLP Engine
  │   ├─ Text Processing
  │   ├─ SIF Taxonomy Matching
  │   └─ LLM Analysis (optional)
  │
  ├─ Risk Engine
  ├─ Recommendation Engine
  └─ MongoDB
      ├─ users
      ├─ safety_reports
      ├─ ai_predictions
      ├─ precursor_detections
      ├─ human_validations
      ├─ recommendations
      ├─ audit_logs
      └─ taxonomy
```

## AI Methodology

The AI engine follows a deterministic-first, LLM-optional approach:

1. **Text Cleaning** - Normalize and clean report text
2. **Keyword/Pattern Analysis** - Match against SIF taxonomy
3. **Hazard Detection** - Identify hazard categories
4. **Exposure Identification** - Detect worker exposure
5. **Control Failure Analysis** - Find safety control gaps
6. **LLM Enhancement** (if configured) - Validate and enrich results
7. **Risk Calculation** - Apply prototype risk methodology
8. **Explainability** - Generate evidence-based explanation
9. **Recommendations** - Suggest safety review actions

**Key Principle**: Never invent evidence. Only report what is actually present in the report text.

See [AI_METHODOLOGY.md](AI_METHODOLOGY.md) for detailed methodology.

## Data and Labeling

### OSHA Data
- **Source**: Public OSHA Severe Injury Reports database
- **Labeling**: NOT ground-truth SIF precursors; injury outcome data only
- **Usage**: Prototype demonstration; clearly labeled in database
- **Important**: Never claimed as OIL operational data

### Synthetic Data
- **Purpose**: Prototype feature demonstration
- **Labeling**: Synthetic labels for development/testing
- **Clearly Marked**: `data_source = "SYNTHETIC_PROTOTYPE"`
- **Coverage**: 100+ diverse workplace scenarios
- **No Fabrication**: Labels use taxonomy rules, not invented expert judgment

See [DATASET.md](DATASET.md) for complete data methodology.

## Limitations

This is a **PROTOTYPE** system. Known limitations:

1. **Not a Prediction System** - Does not predict injury outcomes
2. **Requires Expert Review** - All AI results must be reviewed by safety professionals
3. **Limited Training Data** - Uses OSHA public data and synthetic examples
4. **Taxonomy Constraints** - Covers primary SIF hazard categories
5. **LLM Optional** - Functions with deterministic fallback when no LLM API key
6. **No Real OIL Data** - Demonstrates concept; lacks actual operational context
7. **Prototype Accuracy** - Not scientifically validated; metrics are illustrative

See [LIMITATIONS.md](LIMITATIONS.md) for complete details.

## Database Schema

### Collections

**users**
```json
{
  "user_id": "uuid",
  "email": "string",
  "password_hash": "string",
  "name": "string",
  "role": "admin|safety_officer|manager",
  "created_at": "datetime"
}
```

**safety_reports**
```json
{
  "report_id": "uuid",
  "report_text": "string",
  "report_type": "near_miss|unsafe_act|unsafe_condition",
  "date": "datetime",
  "location": "string",
  "department": "string",
  "activity": "string",
  "data_source": "OSHA|SYNTHETIC_PROTOTYPE",
  "created_at": "datetime"
}
```

**ai_predictions**
```json
{
  "prediction_id": "uuid",
  "report_id": "uuid",
  "sif_status": "YES|NO|UNCERTAIN",
  "confidence": 0-100,
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "hazards": ["array"],
  "exposure": ["array"],
  "control_failures": ["array"],
  "evidence": ["array"],
  "explanation": "string",
  "recommendation": "string",
  "model_type": "RULE_ENGINE|LLM|HYBRID",
  "model_version": "1.0",
  "created_at": "datetime"
}
```

**human_validations**
```json
{
  "validation_id": "uuid",
  "report_id": "uuid",
  "reviewer": "string (email)",
  "ai_decision": "YES|NO|UNCERTAIN",
  "human_decision": "AGREE|DISAGREE|MODIFY",
  "modified_sif_status": "YES|NO|UNCERTAIN",
  "modified_risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "comments": "string",
  "timestamp": "datetime"
}
```

**recommendations**
```json
{
  "recommendation_id": "uuid",
  "report_id": "uuid",
  "category": "LOTO|FALL_PROTECTION|CONFINED_SPACE|etc",
  "action": "string",
  "priority": "LOW|MEDIUM|HIGH|CRITICAL",
  "created_at": "datetime"
}
```

**audit_logs**
```json
{
  "log_id": "uuid",
  "user_id": "uuid",
  "action": "VALIDATE|MODIFY|CONFIRM|etc",
  "report_id": "uuid",
  "timestamp": "datetime",
  "details": "object"
}
```

**taxonomy**
```json
{
  "_id": "ObjectId",
  "categories": {
    "HAZARDOUS_ENERGY": {
      "subcategories": ["Electrical", "Mechanical", "Hydraulic", ...],
      "keywords": ["energized", "high voltage", ...]
    },
    ...
  }
}
```

## Testing

Run tests:
```bash
cd backend
pytest
```

Test coverage:
- Risk engine scoring
- Taxonomy detection
- AI response parsing
- CSV ingestion
- API endpoints
- Database operations

## Development

### Adding New Taxonomy Categories

Edit `data/taxonomy.json` and restart backend.

### Configuring LLM Provider

1. Set environment variables:
   ```
   LLM_PROVIDER=openai
   LLM_API_KEY=sk_xxxxx
   LLM_MODEL=gpt-4
   ```
2. Backend automatically detects and uses LLM
3. Fallback to rule engine if credentials invalid

### Frontend Component Structure

- `/components/common/` - Shared components
- `/components/dashboard/` - Dashboard-specific
- `/components/analysis/` - AI analysis feature
- `/pages/` - Full pages
- `/services/api.js` - API client
- `/hooks/` - Custom hooks

## Performance Notes

- Large OSHA dataset (100k+ rows): Use "Analyze Sample" during demo
- Batch processing: Backend supports async CSV analysis
- Dashboard: Real-time data from MongoDB; no hard-coded values
- Frontend: Lazy loading for reports and analytics

## Contributing

This is a hackathon project. For improvements:

1. Fork the repository
2. Create a feature branch
3. Make changes following the code structure
4. Test thoroughly
5. Document changes
6. Submit pull request

## Future Scope

- OIL-authorized historical safety data
- Domain-specific model fine-tuning
- Multilingual report support
- Voice reporting capability
- Real-time alert system
- Enterprise integration APIs
- Mobile application
- Advanced trend prediction
- Feedback-based model improvement

## Support & Issues

For questions or issues:
- Create an issue on GitHub
- Check documentation files
- Review demo workflow
- Consult LIMITATIONS.md

## License

This project is created for the Smart India Hackathon 2026 and is provided for evaluation purposes.

## Authors

Built for Smart India Hackathon 2026 - Problem Statement SIH26165

---

**Remember**: This is a prototype decision-support system. Always prioritize human expert judgment in workplace safety decisions.
