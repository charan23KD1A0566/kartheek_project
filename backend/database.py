from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import MONGODB_URI, MONGODB_DATABASE
import logging

logger = logging.getLogger(__name__)

# Global MongoDB client and database instances
mongodb_client: AsyncIOMotorClient | None = None
mongodb_db: AsyncIOMotorDatabase | None = None


async def connect_to_mongo():
    """Connect to MongoDB."""
    global mongodb_client, mongodb_db

    try:
        # Create MongoDB client
        mongodb_client = AsyncIOMotorClient(MONGODB_URI)

        # Verify MongoDB connection
        await mongodb_client.admin.command("ping")

        # Select database
        mongodb_db = mongodb_client[MONGODB_DATABASE]

        logger.info(
            f"✓ Connected to MongoDB: {MONGODB_DATABASE}"
        )

        # Create indexes
        await create_indexes()

        print("✓ MongoDB connected and indexes created")

    except Exception as e:
        logger.error(
            f"✗ Failed to connect to MongoDB: {e}"
        )

        # Clean up if connection fails
        if mongodb_client:
            mongodb_client.close()

        mongodb_client = None
        mongodb_db = None

        raise


async def close_mongo_connection():
    """Close MongoDB connection."""
    global mongodb_client, mongodb_db

    try:
        if mongodb_client:
            mongodb_client.close()

            mongodb_client = None
            mongodb_db = None

            logger.info("✓ MongoDB connection closed")

    except Exception as e:
        logger.error(
            f"✗ Error closing MongoDB connection: {e}"
        )


async def create_indexes():
    """Create database indexes for better query performance."""

    if mongodb_db is None:
        logger.warning(
            "Database is not connected. Cannot create indexes."
        )
        return

    try:

        # ==========================================
        # USERS
        # ==========================================

        await mongodb_db.users.create_index(
            "email",
            unique=True
        )


        # ==========================================
        # SAFETY REPORTS
        # ==========================================

        await mongodb_db.safety_reports.create_index(
            "report_id",
            unique=True
        )

        await mongodb_db.safety_reports.create_index(
            "data_source"
        )

        await mongodb_db.safety_reports.create_index(
            "date"
        )

        await mongodb_db.safety_reports.create_index(
            "location"
        )

        await mongodb_db.safety_reports.create_index(
            "created_at"
        )


        # ==========================================
        # AI PREDICTIONS
        # ==========================================

        await mongodb_db.ai_predictions.create_index(
            "report_id"
        )

        await mongodb_db.ai_predictions.create_index(
            "sif_status"
        )

        await mongodb_db.ai_predictions.create_index(
            "risk_level"
        )

        await mongodb_db.ai_predictions.create_index(
            "model_type"
        )

        await mongodb_db.ai_predictions.create_index(
            "created_at"
        )


        # ==========================================
        # HUMAN VALIDATIONS
        # ==========================================

        await mongodb_db.human_validations.create_index(
            "report_id"
        )

        await mongodb_db.human_validations.create_index(
            "reviewer"
        )

        await mongodb_db.human_validations.create_index(
            "timestamp"
        )


        # ==========================================
        # AUDIT LOGS
        # ==========================================

        await mongodb_db.audit_logs.create_index(
            "user_id"
        )

        await mongodb_db.audit_logs.create_index(
            "action"
        )

        await mongodb_db.audit_logs.create_index(
            "timestamp"
        )

        await mongodb_db.audit_logs.create_index(
            "report_id"
        )

        await mongodb_db.alerts.create_index("alert_id", unique=True)
        await mongodb_db.alerts.create_index([("recipients", 1), ("read", 1), ("created_at", -1)])


        # ==========================================
        # TAXONOMY
        # ==========================================

        await mongodb_db.taxonomy.create_index(
            "version"
        )


        logger.info("✓ Indexes created successfully")

    except Exception as e:
        logger.error(
            f"✗ Error creating indexes: {e}"
        )


def get_database() -> AsyncIOMotorDatabase:
    """Return the connected MongoDB database instance."""

    if mongodb_db is None:
        raise RuntimeError(
            "Database not connected. "
            "Call connect_to_mongo() first."
        )

    return mongodb_db