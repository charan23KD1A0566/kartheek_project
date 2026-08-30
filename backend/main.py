"""
SIF Sentinel - Main FastAPI Application
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import uuid4
import os
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Local imports
from config import (
    FRONTEND_API_URL, DEBUG, JWT_SECRET, JWT_ALGORITHM, 
    JWT_EXPIRATION_HOURS, SERVER_HOST, SERVER_PORT, CORS_ORIGINS
)
from database import connect_to_mongo, close_mongo_connection, get_database
from models import (
    LoginRequest, LoginResponse, UserResponse, RegisterRequest, SafetyReportCreate, SafetyReportUpdate,
    AnalyzeRequest,
    SafetyReport, AIAnalysisResult, AIPrediction, HealthResponse,
    DashboardStats, DashboardData, AnalyticsData, HumanValidationInput,
    HumanValidation, UserRole, UploadResponse, UploadStatusResponse, TaxonomyData
)
from services.ai_engine import ai_engine
from services.taxonomy import TaxonomyService
from services.risk_engine import RiskEngine
from utils.auth import create_access_token, verify_token, hash_password, verify_password
from utils.database_helpers import (
    get_user_by_email, create_user, create_report, get_report,
    save_prediction, get_predictions, save_validation
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def serialize_document(value):
    """Convert MongoDB-only values while preserving dates for FastAPI."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {key: serialize_document(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize_document(item) for item in value]
    return value


# ============ Lifecycle Events ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("[START] SIF Sentinel starting up...")
    try:\n        await connect_to_mongo()\n    except Exception as e:\n        logger.warning(f\"Could not connect to MongoDB during startup: {e}\")\n    try:\n        await seed_demo_data()\n    except Exception as e:\n        logger.warning(f\"Could not seed demo data: {e}\")\n    logger.info(\"[OK] SIF Sentinel is ready to serve requests\")\n    yield
    # Shutdown
    logger.info("🛑 SIF Sentinel shutting down...")
    await close_mongo_connection()

app = FastAPI(
    title="SIF Sentinel",
    description="AI/NLP Engine for SIF Precursor Detection",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS] + ["null"],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Auth Endpoints ============

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """User login"""
    try:
        db = get_database()
        user = await get_user_by_email(db, str(credentials.email))
        if not user or not user.get("is_active", True) or not verify_password(credentials.password, user.get("password_hash")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    except HTTPException:
        raise
    except (RuntimeError, ConnectionError) as error:
        logger.error(f"Login database unavailable: {error}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication service is temporarily unavailable")
    except Exception as error:
        logger.exception(f"Login failed unexpectedly: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service failed while processing the request"
        )
    
    # Create token
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=timedelta(hours=JWT_EXPIRATION_HOURS)
    )
    
    logger.info(f"[OK] User logged in: {credentials.email}")
    
    return LoginResponse(
        access_token=access_token,
        user={
            "id": user["user_id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    )


@app.post("/api/auth/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Create an employee account and issue a session token."""
    if request.role != UserRole.EMPLOYEE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Public registration is limited to employees")

    try:
        db = get_database()
        email = str(request.email).strip().lower()
        if await get_user_by_email(db, email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
        user = await create_user(db, email, request.password, request.name.strip(), UserRole.EMPLOYEE.value)
    except HTTPException:
        raise
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    except (RuntimeError, ConnectionError) as error:
        logger.error(f"Registration database unavailable: {error}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Registration service is temporarily unavailable")
    except Exception as error:
        logger.exception(f"Registration failed unexpectedly: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration service failed while creating the account")
    token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=timedelta(hours=JWT_EXPIRATION_HOURS)
    )
    return LoginResponse(
        access_token=token,
        user={"id": user["user_id"], "email": user["email"], "name": user["name"], "role": user["role"]}
    )


# ============ Analysis Endpoints ============

@app.post("/api/analyze", response_model=AIAnalysisResult)
async def analyze_report(
    request: AnalyzeRequest,
    token: str = Depends(verify_token)
):
    """Analyze a safety report"""
    
    if not ai_engine:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI Engine not initialized"
        )
    
    try:
        # Run analysis
        result = ai_engine.analyze_report(request.text)
        logger.info(f"[OK] Analysis complete: {result.sif_status}")
        return result
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.exception("Analysis error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to analyze the report"
        )


@app.post("/api/reports", response_model=dict)
async def create_and_analyze_report(
    report: SafetyReportCreate,
    token: str = Depends(verify_token)
):
    """Create report and analyze it"""
    
    db = get_database()
    
    report_id = None
    alert_id = None

    try:
        user = await get_user_by_email(db, token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        if user.get("role") != UserRole.EMPLOYEE.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only employees can create reports")

        # Create report
        report_id = str(uuid4())
        report_data = {
            "report_id": report_id,
            **report.dict(),
            "date": report.date or datetime.utcnow(),
            "data_source": "USER_SUBMISSION",
            "submitted_by": user["email"],
            "created_at": datetime.utcnow()
        }

        # Analyze report
        analysis = ai_engine.analyze_report(report.report_text)

        await db.safety_reports.insert_one(report_data)
        
        # Save prediction
        prediction_data = {
            "prediction_id": str(uuid4()),
            "report_id": report_id,
            **analysis.dict(),
            "created_at": datetime.utcnow()
        }
        
        await db.ai_predictions.insert_one(prediction_data)

        if analysis.sif_status.value == "YES" and analysis.sif_probability >= 0.55 and analysis.risk_level.value in {"HIGH", "CRITICAL"}:
            alert_id = str(uuid4())
            await db.alerts.insert_one({
                "alert_id": alert_id,
                "report_id": report_id,
                "alert_type": "SIF_PRECURSOR",
                "severity": analysis.risk_level.value,
                "title": "Potential Serious Injury/Fatality Precursor Detected",
                "message": analysis.explanation,
                "risk_level": analysis.risk_level.value,
                "sif_probability": analysis.sif_probability,
                "created_at": datetime.utcnow(),
                "read": False,
                "recipients": [UserRole.MANAGER.value, UserRole.SAFETY_OFFICER.value]
            })

        await db.audit_logs.insert_one({
            "log_id": str(uuid4()),
            "user_id": user["user_id"],
            "action": "CREATE_REPORT",
            "report_id": report_id,
            "timestamp": datetime.utcnow()
        })
        
        logger.info(f"[OK] Report created and analyzed: {report_id}")
        
        return serialize_document({
            "report_id": report_id,
            "message": "Report created and analyzed successfully",
            "analysis": analysis.dict()
        })
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        if report_id:
            await db.safety_reports.delete_one({"report_id": report_id})
            await db.ai_predictions.delete_one({"report_id": report_id})
        if alert_id:
            await db.alerts.delete_one({"alert_id": alert_id})
        logger.exception("Report creation error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create the report"
        )


def _alert_user_can_access(user):
    return user and user.get("role") in {UserRole.MANAGER.value, UserRole.SAFETY_OFFICER.value}


@app.get("/api/alerts")
async def get_alerts(token: str = Depends(verify_token)):
    db = get_database()
    user = await get_user_by_email(db, token)
    if not _alert_user_can_access(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Alert access restricted")
    alerts = await db.alerts.find({"recipients": user["role"]}).sort("created_at", -1).limit(50).to_list(50)
    return serialize_document({"alerts": alerts})


@app.get("/api/alerts/unread")
async def get_unread_alerts(token: str = Depends(verify_token)):
    db = get_database()
    user = await get_user_by_email(db, token)
    if not _alert_user_can_access(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Alert access restricted")
    alerts = await db.alerts.find({"recipients": user["role"], "read": False}).sort("created_at", -1).to_list(50)
    return serialize_document({"alerts": alerts, "count": len(alerts)})


@app.post("/api/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str, token: str = Depends(verify_token)):
    db = get_database()
    user = await get_user_by_email(db, token)
    if not _alert_user_can_access(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Alert access restricted")
    result = await db.alerts.update_one({"alert_id": alert_id, "recipients": user["role"]}, {"$set": {"read": True, "read_at": datetime.utcnow()}})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return {"message": "Alert marked as read"}


@app.get("/api/reports")
async def get_reports(
    skip: int = 0,
    limit: int = 20,
    sif_status: Optional[str] = None,
    risk_level: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """Get reports with optional filtering"""
    
    db = get_database()
    
    try:
        # Build one prediction filter so both query parameters are applied.
        prediction_filter = {}
        
        if sif_status:
            prediction_filter["sif_status"] = sif_status
        
        if risk_level:
            # Find predictions with this risk level
            prediction_filter["risk_level"] = risk_level

        filter_dict = {}
        if prediction_filter:
            predictions = await db.ai_predictions.find(prediction_filter, {"report_id": 1}).to_list(None)
            report_ids = [p["report_id"] for p in predictions]
            filter_dict["report_id"] = {"$in": report_ids}
        
        # Get reports
        reports = await db.safety_reports.find(filter_dict)\
            .sort("created_at", -1)\
            .skip(skip)\
            .limit(limit)\
            .to_list(limit)

        report_ids = [report["report_id"] for report in reports]
        predictions = await db.ai_predictions.find(
            {"report_id": {"$in": report_ids}}
        ).to_list(None) if report_ids else []
        predictions_by_report = {prediction["report_id"]: prediction for prediction in predictions}
        reports = [
            serialize_document({**report, **{
                key: predictions_by_report[report["report_id"]].get(key)
                for key in ("sif_status", "sif_probability", "confidence", "risk_level")
            }})
            if report["report_id"] in predictions_by_report else serialize_document(report)
            for report in reports
        ]
        
        total = await db.safety_reports.count_documents(filter_dict)
        
        return serialize_document({
            "reports": reports,
            "total": total,
            "skip": skip,
            "limit": limit
        })
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.exception("Error fetching reports")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load reports"
        )


@app.get("/api/reports/{report_id}")
async def get_report_detail(
    report_id: str,
    token: str = Depends(verify_token)
):
    """Get report details with analysis"""
    
    db = get_database()
    
    try:
        # Get report
        report = await db.safety_reports.find_one({"report_id": report_id})
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Get prediction
        prediction = await db.ai_predictions.find_one({"report_id": report_id})
        
        # Get validation if exists
        validation = await db.human_validations.find_one({"report_id": report_id})
        
        return serialize_document({
            "report": report,
            "prediction": prediction,
            "validation": validation
        })
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.exception("Error fetching report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load the report"
        )


@app.put("/api/reports/{report_id}")
async def update_report(
    report_id: str,
    report_update: SafetyReportUpdate,
    token: str = Depends(verify_token)
):
    """Update report metadata without replacing the stored AI analysis."""

    db = get_database()

    try:
        report = await db.safety_reports.find_one({"report_id": report_id})
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        user = await get_user_by_email(db, token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        if user.get("role") not in {UserRole.ADMIN.value, UserRole.SAFETY_OFFICER.value}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authorization required")

        update_payload = {k: v for k, v in report_update.dict(exclude_unset=True).items() if v is not None}
        if not update_payload:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No report updates provided")

        if "report_text" in update_payload and len(update_payload["report_text"].strip()) < 10:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Report description must be at least 10 characters.")

        update_payload["updated_at"] = datetime.utcnow()
        await db.safety_reports.update_one({"report_id": report_id}, {"$set": update_payload})

        await db.audit_logs.insert_one({
            "log_id": str(uuid4()),
            "user_id": user["user_id"],
            "action": "UPDATE_REPORT",
            "report_id": report_id,
            "timestamp": datetime.utcnow(),
            "details": update_payload
        })

        logger.info(f"[OK] Report updated: {report_id}")
        return serialize_document({"message": "Report updated successfully", "report_id": report_id})

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.exception("Report update error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update the report"
        )


# ============ Validation Endpoints ============

@app.post("/api/reports/{report_id}/validate")
async def validate_report(
    report_id: str,
    validation_input: HumanValidationInput,
    token: str = Depends(verify_token)
):
    """Human validation of report analysis"""
    
    db = get_database()
    
    try:
        report = await db.safety_reports.find_one({"report_id": report_id}, {"_id": 1})
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        # Get authenticated reviewer from the token subject.
        user = await get_user_by_email(db, token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        if user.get("role") not in {UserRole.ADMIN.value, UserRole.SAFETY_OFFICER.value}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Safety-officer authorization required")

        prediction = await db.ai_predictions.find_one({"report_id": report_id}, {"sif_status": 1})
        if not prediction:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Report has no analysis to validate")
        if validation_input.ai_decision.value != prediction["sif_status"]:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="AI decision does not match stored analysis")
        if validation_input.human_decision.value == "MODIFY":
            if not validation_input.modified_sif_status or not validation_input.modified_risk_level:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Modified SIF status and risk level are required for MODIFY",
                )
            if not validation_input.comments or not validation_input.comments.strip():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Reviewer comments are required for MODIFY",
                )
        
        # Save validation
        validation_data = {
            "validation_id": str(uuid4()),
            "report_id": report_id,
            **validation_input.dict(),
            "reviewer": user["email"],
            "timestamp": datetime.utcnow()
        }
        
        existing_validation = await db.human_validations.find_one(
            {"report_id": report_id, "reviewer": user["email"]}
        )
        if existing_validation:
            await db.human_validations.update_one(
                {"_id": existing_validation["_id"]},
                {"$set": validation_data}
            )
            validation_data["validation_id"] = existing_validation["validation_id"]
        else:
            await db.human_validations.insert_one(validation_data)
        
        # Log audit
        await db.audit_logs.insert_one({
            "log_id": str(uuid4()),
            "user_id": user["user_id"],
            "action": "VALIDATE",
            "report_id": report_id,
            "timestamp": datetime.utcnow(),
            "details": validation_data
        })
        
        logger.info(f"[OK] Report validated: {report_id}")
        
        return serialize_document({
            "message": "Validation recorded successfully",
            "validation_id": validation_data["validation_id"]
        })
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.exception("Validation error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save validation"
        )


# ============ Dashboard Endpoints ============

@app.get("/api/dashboard", response_model=DashboardData)
async def get_dashboard(token: str = Depends(verify_token)):
    """Get dashboard statistics"""
    
    db = get_database()
    
    try:
        # Get counts
        total_reports = await db.safety_reports.count_documents({})
        
        # Get SIF precursors
        sif_yes = await db.ai_predictions.count_documents({"sif_status": "YES"})
        sif_uncertain = await db.ai_predictions.count_documents({"sif_status": "UNCERTAIN"})
        
        # Get risk levels
        high_risk = await db.ai_predictions.count_documents({"risk_level": "HIGH"})
        critical_risk = await db.ai_predictions.count_documents({"risk_level": "CRITICAL"})
        
        # Get pending validation
        prediction_ids = await db.ai_predictions.distinct("report_id")
        validated_ids = await db.human_validations.distinct("report_id")
        pending_validation = len(set(prediction_ids) - set(validated_ids))
        validated = len(set(prediction_ids) & set(validated_ids))
        
        # Calculate agreement rate
        agreement_rate = 0.0
        validations_total = await db.human_validations.count_documents({})
        if validations_total > 0:
            agreed = await db.human_validations.count_documents(
                {"human_decision": "AGREE"}
            )
            agreement_rate = (agreed / validations_total) * 100
        
        stats = DashboardStats(
            total_reports=total_reports,
            potential_sif_precursors=sif_yes + sif_uncertain,
            high_risk_reports=high_risk,
            critical_risk_reports=critical_risk,
            pending_validation=pending_validation,
            validated_reports=validated,
            validation_agreement_rate=agreement_rate
        )
        
        # Get recent reports
        recent = await db.safety_reports.find()\
            .sort("created_at", -1)\
            .limit(5)\
            .to_list(5)
        recent = [
            serialize_document({**report, "date": report.get("date", report.get("created_at"))})
            for report in recent
        ]
        
        return DashboardData(stats=stats, recent_reports=recent)
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============ Analytics Endpoints ============

@app.get("/api/analytics", response_model=AnalyticsData)
async def get_analytics(token: str = Depends(verify_token)):
    """Get analytics data"""
    
    db = get_database()
    
    try:
        # Total reports
        total = await db.safety_reports.count_documents({})
        
        # SIF percentage
        sif_count = await db.ai_predictions.count_documents({"sif_status": "YES"})
        sif_percentage = (sif_count / total * 100) if total > 0 else 0
        
        # Risk distribution
        risk_dist = {}
        for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            risk_dist[level] = await db.ai_predictions.count_documents(
                {"risk_level": level}
            )
        
        # Hazard distribution
        hazards_raw = await db.ai_predictions.find({}).to_list(None)
        hazard_counts = {}
        for pred in hazards_raw:
            for hazard in pred.get("hazards", []):
                hazard_counts[hazard] = hazard_counts.get(hazard, 0) + 1
        
        hazard_dist = [
            {
                "hazard": h,
                "count": c,
                "percentage": (c / total * 100) if total > 0 else 0
            }
            for h, c in sorted(hazard_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Validation agreement
        validations = await db.human_validations.find({}).to_list(None)
        agreement = 0.0
        if validations:
            agreed = sum(1 for v in validations if v.get("human_decision") == "AGREE")
            agreement = (agreed / len(validations)) * 100
        
        # Data source distribution
        data_sources = {}
        reports = await db.safety_reports.find({}).to_list(None)
        for r in reports:
            ds = r.get("data_source", "UNKNOWN")
            data_sources[ds] = data_sources.get(ds, 0) + 1
        
        # Reports over time (simplified - last 7 days)
        from datetime import datetime, timedelta
        reports_over_time = []
        for i in range(6, -1, -1):
            date = (datetime.utcnow() - timedelta(days=i)).date()
            count = await db.safety_reports.count_documents({
                "created_at": {
                    "$gte": datetime.combine(date, datetime.min.time()),
                    "$lt": datetime.combine(date, datetime.max.time())
                }
            })
            reports_over_time.append({
                "date": date.isoformat(),
                "count": count
            })
        
        return AnalyticsData(
            total_reports=total,
            sif_percentage=sif_percentage,
            risk_distribution=risk_dist,
            hazard_distribution=hazard_dist,
            validation_agreement=agreement,
            data_source_distribution=data_sources,
            reports_over_time=reports_over_time
        )
    
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============ Taxonomy Endpoint ============

@app.get("/api/taxonomy")
async def get_taxonomy(token: str = Depends(verify_token)):
    """Get SIF taxonomy"""
    
    try:
        taxonomy = TaxonomyService.load_taxonomy()
        return {
            "categories": taxonomy.get("categories", {}),
            "patterns": taxonomy.get("precursor_patterns", []),
            "version": taxonomy.get("version", "1.0")
        }
    except Exception as e:
        logger.error(f"Taxonomy error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============ Health Check ============

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        db = get_database()
        await db.client.admin.command("ping")
        return HealthResponse(status="healthy", database="connected")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            database="disconnected",
            version="1.0"
        )


# ============ Seed Demo Data ============

async def seed_demo_data():
    """Seed database with demo users and data"""
    
    db = get_database()
    
    try:
        logger.info("Seeding database with demo data...")
        
        # Create demo users
        demo_users = [
            {
                "user_id": str(uuid4()),
                "email": "admin@sifsentinel.demo",
                "password_hash": hash_password("Admin@123"),
                "name": "Admin User",
                "role": UserRole.ADMIN.value,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "user_id": str(uuid4()),
                "email": "safety@sifsentinel.demo",
                "password_hash": hash_password("Safety@123"),
                "name": "Safety Officer",
                "role": UserRole.SAFETY_OFFICER.value,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "user_id": str(uuid4()),
                "email": "employee@sifsentinel.demo",
                "password_hash": hash_password("Employee@123"),
                "name": "Field Employee",
                "role": UserRole.EMPLOYEE.value,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "user_id": str(uuid4()),
                "email": "manager@sifsentinel.demo",
                "password_hash": hash_password("Manager@123"),
                "name": "Manager",
                "role": UserRole.MANAGER.value,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
        ]
        
        for demo_user in demo_users:
            await db.users.update_one(
                {"email": demo_user["email"]},
                {"$set": {
                    "name": demo_user["name"],
                    "password_hash": demo_user["password_hash"],
                    "role": demo_user["role"],
                    "is_active": True,
                    "updated_at": datetime.utcnow(),
                }, "$setOnInsert": {
                    "user_id": demo_user["user_id"],
                    "email": demo_user["email"],
                    "created_at": demo_user["created_at"],
                }},
                upsert=True
            )
        logger.info(f"[OK] Ensured {len(demo_users)} demo users")
        
        # Create demo report
        demo_report_id = "demo-energized-equipment-001"
        demo_report = {
            "report_id": demo_report_id,
            "report_text": "During maintenance, a worker entered an energized equipment area without completing the required isolation procedure.",
            "report_type": "unsafe_act",
            "location": "Workshop Area A",
            "department": "Maintenance",
            "activity": "Equipment Maintenance",
            "data_source": "USER_SUBMISSION",
            "created_at": datetime.utcnow()
        }
        
        await db.safety_reports.update_one(
            {"report_id": demo_report_id},
            {"$setOnInsert": demo_report},
            upsert=True
        )
        
        # Analyze demo report
        if ai_engine:
            analysis = ai_engine.analyze_report(demo_report["report_text"])
            
            demo_prediction = {
                "prediction_id": str(uuid4()),
                "report_id": demo_report_id,
                **analysis.dict(),
                "created_at": datetime.utcnow()
            }
            
            await db.ai_predictions.update_one(
                {"report_id": demo_report_id},
                {"$setOnInsert": demo_prediction},
                upsert=True
            )
            logger.info("[OK] Ensured demo report with analysis")
        
        # Seed taxonomygit --version
        taxonomy = TaxonomyService.load_taxonomy()
        await db.taxonomy.replace_one(
            {"_id": taxonomy.get("_id", "sif_taxonomy_v1")},
            taxonomy,
            upsert=True
        )
        logger.info("[OK] Taxonomy ensured")
        
        logger.info("[OK] Database seeding complete")
    
    except Exception as e:
        logger.error(f"Seeding error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info" if DEBUG else "warning"
    )
