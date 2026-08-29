# SIF SENTINEL - SYSTEM ARCHITECTURE

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│                     React + Vite + TailwindCSS                   │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │   Login      │  Dashboard   │  AI Analysis │  Reports     │  │
│  │   Component  │  Component   │  Component   │  Component   │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (HTTPS/REST)
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                            │
│                      FastAPI + Pydantic                           │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │ Auth Routes  │ Report Routes│ Analysis API │ Admin API    │  │
│  │ /auth/*      │ /api/reports │ /api/analyze │ /api/admin   │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (Internal)
┌─────────────────────────────────────────────────────────────────┐
│                  APPLICATION LOGIC LAYER                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              SIF Sentinel AI/NLP Engine                     │ │
│  │  ┌──────────────┬──────────────┬──────────────────────┐   │ │
│  │  │Text Cleaner  │ Evidence     │ Hazard Detection    │   │ │
│  │  │& Normalizer  │ Extractor    │ (Taxonomy Matching) │   │ │
│  │  └──────────────┴──────────────┴──────────────────────┘   │ │
│  │  ┌──────────────┬──────────────┬──────────────────────┐   │ │
│  │  │Exposure ID   │ Control      │ Risk Scoring &      │   │ │
│  │  │              │ Failure Det. │ Recommendation Gen. │   │ │
│  │  └──────────────┴──────────────┴──────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Business Logic Services                        │ │
│  │  ┌──────────────┬──────────────┬──────────────────────┐   │ │
│  │  │Report Service│ User Service │ Validation Service  │   │ │
│  │  │              │              │                      │   │ │
│  │  └──────────────┴──────────────┴──────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (Async I/O)
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                               │
│                      MongoDB (Document DB)                        │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │ users        │ reports      │ analyses     │ validations  │  │
│  │ collection   │ collection   │ collection   │ collection   │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Frontend (React + Vite)

**Location**: `/frontend`

**Key Files**:
```
frontend/
├── src/
│   ├── components/
│   │   ├── LoginForm.tsx       # Authentication UI
│   │   ├── Dashboard.tsx        # Main dashboard
│   │   ├── AnalysisForm.tsx     # AI analysis input
│   │   ├── ReportList.tsx       # Report table view
│   │   ├── ReportDetail.tsx     # Single report view
│   │   ├── Analytics.tsx        # Analytics visualizations
│   │   └── Navigation.tsx       # App navigation
│   ├── services/
│   │   ├── api.ts              # API client
│   │   └── auth.ts             # Auth service
│   ├── App.tsx                 # Main app component
│   ├── main.tsx                # Entry point
│   └── index.css               # Global styles
├── .env.example                # Environment template
├── package.json                # Dependencies
└── vite.config.ts              # Vite config
```

**Technology Stack**:
- React 18 (UI library)
- Vite (build tool)
- TailwindCSS (styling)
- Recharts (visualizations)
- Axios (HTTP client)
- TypeScript (type safety)

**Key Features**:
- ✓ Component-based architecture
- ✓ TypeScript for type safety
- ✓ Responsive design (mobile + desktop)
- ✓ Chart visualization library
- ✓ API error handling
- ✓ Loading states & spinners
- ✓ Form validation

### 2. Backend (FastAPI + Pydantic)

**Location**: `/backend`

**Key Files**:
```
backend/
├── main.py                     # FastAPI app + routes
├── database.py                 # MongoDB connection
├── models.py                   # Pydantic data models
├── auth.py                     # JWT authentication
├── sif_engine.py               # AI/NLP core engine
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── data/
    ├── taxonomy.json           # SIF taxonomy
    ├── recommendations.json    # Risk recommendations
    └── synthetic_reports.json  # Demo data
```

**Core Routes**:

```
POST   /auth/login              # User login
POST   /auth/register           # User registration (if enabled)
GET    /api/health              # Health check

GET    /api/reports             # List reports
POST   /api/reports             # Create report
GET    /api/reports/{id}        # Get report
PUT    /api/reports/{id}        # Update report
DELETE /api/reports/{id}        # Delete report (admin)

POST   /api/analyze             # Analyze report
GET    /api/analytics           # Get analytics data
POST   /api/validate/{id}       # Validate analysis

GET    /api/admin/users         # List users (admin)
POST   /api/admin/seed          # Seed demo data (admin)
GET    /docs                    # Swagger UI
GET    /openapi.json            # OpenAPI spec
```

**Technology Stack**:
- FastAPI (web framework)
- Pydantic (data validation)
- Motor (async MongoDB driver)
- PyJWT (JWT authentication)
- Python 3.10+
- asyncio (async programming)

**Architecture Patterns**:
- ✓ Async/await for all I/O
- ✓ Dependency injection (FastAPI)
- ✓ Pydantic models for validation
- ✓ Custom exceptions with error codes
- ✓ Middleware for error handling
- ✓ CORS configuration
- ✓ Rate limiting ready (not implemented)

### 3. SIF Engine (AI/NLP Core)

**Location**: `/backend/sif_engine.py`

**Architecture**:

```
ReportAnalyzer
├── __init__()
│   ├── Load taxonomy
│   ├── Load recommendations
│   └── Initialize patterns
│
├── analyze(report_text)
│   ├── clean_text()
│   ├── extract_evidence()
│   ├── detect_hazards()
│   ├── identify_exposure()
│   ├── identify_control_failures()
│   ├── calculate_sif_status()
│   ├── calculate_risk_score()
│   ├── generate_recommendations()
│   ├── generate_explanation()
│   └── return(AnalysisResult)
│
├── detect_hazards()
│   ├── Check HAZARDOUS_ENERGY
│   ├── Check WORKING_AT_HEIGHT
│   ├── Check LINE_OF_FIRE
│   ├── Check CONFINED_SPACE
│   ├── Check VEHICLE_MOBILE_EQUIPMENT
│   └── Check CRITICAL_CONTROL_FAILURE
│
└── Helper methods
    ├── match_keyword()
    ├── get_exposure_from_evidence()
    ├── get_control_failures()
    └── calculate_confidence()
```

**Key Classes**:

```python
class HazardCategory(Enum):
    """All possible hazard categories"""
    HAZARDOUS_ENERGY = "hazardous_energy"
    WORKING_AT_HEIGHT = "working_at_height"
    LINE_OF_FIRE = "line_of_fire"
    CONFINED_SPACE = "confined_space"
    VEHICLE_MOBILE_EQUIPMENT = "vehicle_mobile_equipment"
    CRITICAL_CONTROL_FAILURE = "critical_control_failure"

class ExposureType(Enum):
    """Exposure classification"""
    DIRECT_CONTACT = "direct_contact"
    FULL_EXPOSURE = "full_exposure"
    PARTIAL_EXPOSURE = "partial_exposure"
    PROXIMITY = "proximity"
    REPEATED_EXPOSURE = "repeated_exposure"

class ControlFailure(Enum):
    """Types of control failures"""
    LOTO_ISOLATION_FAILURE = "loto_isolation_failure"
    PERMIT_FAILURE = "permit_failure"
    PPE_FAILURE = "ppe_failure"
    BARRIER_BYPASS = "barrier_bypass"
    PROCEDURE_VIOLATION = "procedure_violation"
    LACK_OF_MONITORING = "lack_of_monitoring"

class AnalysisResult(BaseModel):
    """Output of AI analysis"""
    sif_status: str  # YES, NO, UNCERTAIN
    confidence: float  # 0-100
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    hazards: List[str]  # Detected categories
    exposure: str  # Exposure type
    control_failures: List[str]  # Failures detected
    evidence: List[str]  # Key quotes from report
    explanation: str  # Reasoning
    recommendations: List[str]  # Action items
    model_info: Dict  # Model version & info
```

**Processing Pipeline**:

1. **Text Cleaning** (15 operations)
   - Lowercase conversion
   - Whitespace normalization
   - Special character handling
   - Sentence extraction

2. **Evidence Extraction** (5-10 key sentences)
   - Identify decision-relevant text
   - Preserve original quotes
   - Limit to relevant portions

3. **Hazard Detection** (Rule-based)
   - Iterate through taxonomy
   - Match keywords with word boundaries
   - Count matches per category
   - Accumulate detected hazards

4. **Exposure Identification** (5 types)
   - Match exposure keywords
   - Map to exposure type
   - Infer from context
   - Assign confidence

5. **Control Failure Detection** (6 types)
   - Identify missing controls
   - Match failure patterns
   - Link to hazards
   - Prioritize failures

6. **SIF Status Decision** (Decision tree)
   - Low-risk heuristics → NO
   - No hazards → NO
   - Multiple conditions → Decision tree
   - Return with confidence

7. **Risk Scoring** (Weighted model)
   - Hazard severity (35%)
   - Exposure severity (25%)
   - Control failure (30%)
   - Consequence potential (10%)
   - Map to CRITICAL/HIGH/MEDIUM/LOW

8. **Explanation Generation** (Evidence-based)
   - Structure reasoning
   - Quote exact evidence
   - List detected components
   - Include confidence caveat

9. **Recommendation Generation** (Taxonomy-based)
   - Map hazards to recommendations
   - Map controls to improvements
   - Sort by priority
   - Limit to top 5

10. **Result Assembly**
    - Create AnalysisResult object
    - Include all metadata
    - Add model version
    - Return to API

**Performance**:
- Text processing: ~5ms
- Hazard detection: ~50ms
- Control analysis: ~30ms
- Risk calculation: ~10ms
- Total: ~100-150ms per report

### 4. Database Layer (MongoDB)

**Collections**:

#### Users Collection
```json
{
  "_id": ObjectId(),
  "username": "admin@sifsentinel.demo",
  "email": "admin@sifsentinel.demo",
  "password_hash": "bcrypt_hash",
  "role": "admin",  // admin, safety_officer, manager
  "created_at": ISODate(),
  "updated_at": ISODate(),
  "is_active": true
}
```

#### Reports Collection
```json
{
  "_id": ObjectId(),
  "report_text": "During maintenance, a worker...",
  "report_type": "unsafe_act",  // unsafe_act, unsafe_condition, near_miss
  "location": "Workshop Area A",
  "department": "Maintenance",
  "activity": "Equipment Maintenance",
  "data_source": "synthetic",  // osha, user_input, synthetic
  "created_at": ISODate(),
  "updated_by": ObjectId(),  // User reference
  "is_analyzed": true,
  "ai_analysis": {
    "sif_status": "YES",
    "confidence": 85,
    "risk_level": "HIGH",
    "analyzed_at": ISODate()
  }
}
```

#### Analyses Collection
```json
{
  "_id": ObjectId(),
  "report_id": ObjectId(),
  "sif_status": "YES",
  "confidence": 85,
  "risk_level": "HIGH",
  "hazards": ["hazardous_energy"],
  "exposure": "full_exposure",
  "control_failures": ["loto_isolation_failure"],
  "evidence": ["entered an energized equipment area"],
  "explanation": "Potential SIF precursor detected...",
  "recommendations": ["Verify all energy isolation procedures..."],
  "model_version": "1.0",
  "model_type": "rule_engine",
  "created_at": ISODate(),
  "created_by": ObjectId()
}
```

#### Validations Collection
```json
{
  "_id": ObjectId(),
  "analysis_id": ObjectId(),
  "report_id": ObjectId(),
  "validator_decision": "agree",  // agree, disagree, uncertain
  "validated_at": ISODate(),
  "validated_by": ObjectId(),
  "comments": "Concur with SIF assessment...",
  "agreed_risk_level": "HIGH",
  "corrections": {}
}
```

**Indexes**:
- `reports`: report_type, data_source, created_at
- `analyses`: report_id, sif_status, risk_level
- `validations`: report_id, validated_at
- `users`: email (unique), username (unique)

---

## API Contract

### 1. Authentication

**POST /auth/login**
```json
Request:
{
  "username": "admin@sifsentinel.demo",
  "password": "Admin@123"
}

Response (200):
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "username": "admin@sifsentinel.demo",
    "role": "admin"
  }
}
```

### 2. Report Management

**POST /api/reports**
```json
Request:
{
  "report_text": "During maintenance...",
  "report_type": "unsafe_act",
  "location": "Workshop Area A",
  "department": "Maintenance",
  "activity": "Equipment Maintenance"
}

Response (201):
{
  "id": "507f1f77bcf86cd799439011",
  "report_text": "During maintenance...",
  "report_type": "unsafe_act",
  "created_at": "2024-01-01T10:00:00Z",
  "is_analyzed": false
}
```

**GET /api/reports**
```
Query Params:
  ?sif_status=YES
  ?risk_level=HIGH
  ?skip=0
  ?limit=10
  ?sort=-created_at

Response (200):
{
  "total": 25,
  "reports": [
    { report_object... },
    { report_object... }
  ]
}
```

### 3. AI Analysis

**POST /api/analyze**
```json
Request:
{
  "report_text": "During maintenance..."
}

Response (200):
{
  "sif_status": "YES",
  "confidence": 85,
  "risk_level": "HIGH",
  "hazards": ["hazardous_energy"],
  "exposure": "full_exposure",
  "control_failures": ["loto_isolation_failure"],
  "evidence": ["entered an energized equipment area"],
  "explanation": "Potential SIF precursor detected...",
  "recommendations": ["Verify all energy isolation procedures..."],
  "model_info": {
    "version": "1.0",
    "type": "rule_engine"
  }
}
```

### 4. Analytics

**GET /api/analytics**
```json
Response (200):
{
  "total_reports": 25,
  "sif_precursors": 5,
  "critical_risk": 3,
  "pending_validation": 8,
  "hazard_distribution": {
    "hazardous_energy": 8,
    "working_at_height": 5,
    "line_of_fire": 4,
    "confined_space": 2
  },
  "risk_distribution": {
    "critical": 3,
    "high": 7,
    "medium": 10,
    "low": 5
  },
  "reports_by_date": [
    { "date": "2024-01-01", "count": 2 },
    { "date": "2024-01-02", "count": 3 }
  ]
}
```

---

## Data Flow Diagrams

### User Upload & Analysis Flow

```
User Input Report
    ↓
Validation (Pydantic)
    ↓
Save to MongoDB (Reports collection)
    ↓
Trigger AI Analysis
    ├→ Clean text
    ├→ Extract evidence
    ├→ Detect hazards
    ├→ Identify exposure
    ├→ Identify control failures
    ├→ Calculate SIF status
    ├→ Generate explanation
    └→ Generate recommendations
    ↓
Save Analysis (Analyses collection)
    ↓
Return to Frontend
    ↓
Display Results
    ↓
User Validates
    ↓
Save Validation (Validations collection)
    ↓
Update Dashboard Analytics
```

### Authentication Flow

```
Frontend Login Form
    ↓
POST /auth/login
    ↓
Verify Credentials (MongoDB)
    ↓
Hash Password Check
    ↓
Generate JWT
    ↓
Return Token + User Info
    ↓
Frontend Stores Token (localStorage)
    ↓
Add to Subsequent Requests (Authorization header)
    ↓
Backend Validates Token
    ↓
Check Expiration + Signature
    ↓
Route Request or 401 Unauthorized
```

### Dashboard Metrics Calculation

```
Frontend Requests Analytics
    ↓
GET /api/analytics
    ↓
Query MongoDB (Aggregation Pipeline)
    ├→ Count total reports
    ├→ Count SIF=YES reports
    ├→ Count CRITICAL risk reports
    ├→ Group by hazard type
    ├→ Group by risk level
    └→ Group by date (last 7 days)
    ↓
Calculate Percentages
    ↓
Format for Charts
    ↓
Return JSON
    ↓
Frontend Renders Charts (Recharts)
```

---

## Deployment Architecture

### Development Setup
```
Local Machine
├── Frontend (npm run dev)
│   └── http://localhost:5173
├── Backend (uvicorn)
│   └── http://localhost:8000
└── MongoDB (docker-compose)
    └── localhost:27017
```

### Docker Compose

**Services**:
1. **mongodb**: Official MongoDB image
   - Port: 27017
   - Volume: data persistence
   - Health check: mongosh commands
   - Initialization: Seed script runs on startup

2. **Frontend**: Would use Node image
   - Port: 3000
   - Depends on backend

3. **Backend**: Would use Python image
   - Port: 8000
   - Depends on MongoDB
   - Environment: .env file

### Production Architecture (Recommended)

```
                    DNS
                     ↓
              Load Balancer (SSL)
              /           \
        API Server 1   API Server 2   (FastAPI)
             \           /
         MongoDB Cluster
         ├── Primary
         ├── Secondary 1
         └── Secondary 2
         
CDN for Frontend Assets
    ↓
Static Site (S3 / CloudFront)
    ↓
React SPA
```

---

## Security Architecture

### Authentication
- JWT tokens (RS256 signing)
- 24-hour expiration
- Refresh token mechanism
- Role-based access control (RBAC)

### Authorization
- Roles: admin, safety_officer, manager
- Route-level permissions
- Resource-level permissions
- Audit logging for sensitive operations

### Data Protection
- Password hashing (bcrypt)
- HTTPS only (production)
- Input validation (Pydantic)
- SQL injection prevention (MongoDB parameterized)
- CSRF protection
- CORS configuration

### Monitoring
- Request logging
- Error tracking
- Database query logging
- Authentication attempt logging
- API rate limiting (future)

---

## Scalability Considerations

### Current Limitations
- Single MongoDB instance
- Single API server
- Frontend static assets not cached
- No database replication

### Scaling Strategies
1. **Horizontal API Scaling**
   - Add load balancer
   - Multiple FastAPI instances
   - Shared MongoDB connection pool

2. **Database Scaling**
   - MongoDB replication set
   - Sharding for large datasets
   - Indexing optimization

3. **Frontend Scaling**
   - CDN for static assets
   - Edge caching
   - Compression

4. **AI Engine Optimization**
   - Parallel report analysis
   - Caching taxonomy matches
   - Async analysis for bulk uploads

---

## Monitoring & Observability

### Current State
- Basic logging
- Health check endpoint
- Error responses

### Future Additions
- Application Performance Monitoring (APM)
- Centralized logging (ELK stack)
- Distributed tracing
- Metrics collection (Prometheus)
- Alerting system
- Real-time dashboards
- User session tracking

---

## Technology Decisions & Rationale

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Frontend | React | Component reusability, ecosystem, developer experience |
| Frontend Builder | Vite | Fast HMR, modern bundling, ES modules |
| Styling | TailwindCSS | Utility-first, rapid development, consistent design |
| Backend | FastAPI | Async support, automatic API docs, Pydantic integration |
| Database | MongoDB | Flexible schema, good for prototyping, scalable |
| Auth | JWT | Stateless, scalable, industry standard |
| NLP Engine | Rule-based | Deterministic, explainable, works offline |
| API Format | REST | Standard, familiar, JSON payloads |

---

**Architecture Version**: 1.0  
**Last Updated**: 2024-01-01  
**For**: Smart India Hackathon 2026 - SIH26165
