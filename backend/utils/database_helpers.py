"""
Database helper functions
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
from utils.auth import hash_password
import logging

logger = logging.getLogger(__name__)


async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[Dict]:
    """Get user by email"""
    return await db.users.find_one({"email": email.strip().lower()})


async def create_user(
    db: AsyncIOMotorDatabase,
    email: str,
    password: str,
    name: str,
    role: str = "EMPLOYEE"
) -> Dict:
    """Create new user"""
    
    user = {
        "user_id": str(uuid4()),
        "email": email.strip().lower(),
        "password_hash": hash_password(password),
        "name": name,
        "role": role,
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    await db.users.insert_one(user)
    logger.info(f"User created: {email}")
    return user


async def create_report(
    db: AsyncIOMotorDatabase,
    report_text: str,
    report_type: str,
    location: Optional[str] = None,
    department: Optional[str] = None,
    activity: Optional[str] = None,
    date: Optional[datetime] = None,
    data_source: str = "USER_SUBMISSION"
) -> str:
    """Create safety report"""
    
    report_id = str(uuid4())
    
    report = {
        "report_id": report_id,
        "report_text": report_text,
        "report_type": report_type,
        "location": location,
        "department": department,
        "activity": activity,
        "date": date or datetime.utcnow(),
        "data_source": data_source,
        "created_at": datetime.utcnow()
    }
    
    await db.safety_reports.insert_one(report)
    logger.info(f"Report created: {report_id}")
    return report_id


async def get_report(db: AsyncIOMotorDatabase, report_id: str) -> Optional[Dict]:
    """Get report by ID"""
    return await db.safety_reports.find_one({"report_id": report_id})


async def save_prediction(
    db: AsyncIOMotorDatabase,
    report_id: str,
    analysis_result: Dict
) -> str:
    """Save AI prediction"""
    
    prediction = {
        "prediction_id": str(uuid4()),
        "report_id": report_id,
        **analysis_result,
        "created_at": datetime.utcnow()
    }
    
    await db.ai_predictions.insert_one(prediction)
    logger.info(f"Prediction saved for report: {report_id}")
    return prediction["prediction_id"]


async def get_predictions(
    db: AsyncIOMotorDatabase,
    report_id: str
) -> Optional[Dict]:
    """Get predictions for a report"""
    return await db.ai_predictions.find_one({"report_id": report_id})


async def save_validation(
    db: AsyncIOMotorDatabase,
    report_id: str,
    reviewer: str,
    ai_decision: str,
    human_decision: str,
    modified_sif_status: Optional[str] = None,
    modified_risk_level: Optional[str] = None,
    comments: Optional[str] = None
) -> str:
    """Save human validation"""
    
    validation = {
        "validation_id": str(uuid4()),
        "report_id": report_id,
        "reviewer": reviewer,
        "ai_decision": ai_decision,
        "human_decision": human_decision,
        "modified_sif_status": modified_sif_status,
        "modified_risk_level": modified_risk_level,
        "comments": comments,
        "timestamp": datetime.utcnow()
    }
    
    await db.human_validations.insert_one(validation)
    logger.info(f"Validation saved for report: {report_id}")
    return validation["validation_id"]
