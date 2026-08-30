"""
AI Engine - Main NLP/SIF analysis pipeline
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple

from models import SIFStatus, RiskLevel, AIAnalysisResult, ModelType
from services.taxonomy import TaxonomyService
from services.risk_engine import RiskEngine
from services.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

try:
    import joblib
except ImportError:
    joblib = None


class AIEngine:
    """
    Main AI/NLP Engine for SIF Precursor Analysis.

    Pipeline:
    1. Text cleaning and normalization
    2. ML probability prediction
    3. Hazard detection via taxonomy matching
    4. Exposure detection
    5. Control failure detection
    6. Evidence extraction
    7. Safety-critical rule evaluation
    8. SIF status and probability calculation
    9. Risk scoring
    10. Explanation generation
    11. Recommendation generation
    """

    def __init__(self):
        """Initialize AI engine with taxonomy."""
        try:
            self.taxonomy = TaxonomyService.load_taxonomy()
            self.categories = TaxonomyService.get_categories()
            self.patterns = TaxonomyService.get_precursor_patterns()
            self.avoid_keywords = TaxonomyService.get_keywords_to_avoid()
            logger.info("[OK] AI Engine initialized with taxonomy")
        except Exception as e:
            logger.warning(f"Failed to load taxonomy for AI Engine: {e}. Using minimal defaults.")
            self.taxonomy = TaxonomyService._get_fallback_taxonomy()
            self.categories = self.taxonomy.get("categories", {})
            self.patterns = self.taxonomy.get("precursor_patterns", [])
            self.avoid_keywords = self.taxonomy.get("keywords_to_avoid", [])
        self.ml_model = self._load_ml_model()

    # =============================================================
    # MODEL LOADING
    # =============================================================

    def _load_ml_model(self):
        """Load trained ML model if available."""

        if joblib is None:
            logger.warning(
                "ML dependencies are unavailable; using taxonomy/rule fallback"
            )
            return None

        model_path = (
            Path(__file__).resolve().parent.parent
            / "models"
            / "sif_model.joblib"
        )

        if not model_path.exists():
            logger.warning(
                "Trained model artifact not found: %s",
                model_path
            )
            return None

        try:
            model = joblib.load(model_path)

            logger.info(
                "Loaded trained SIF model: %s",
                model_path
            )

            return model

        except Exception:
            logger.exception(
                "Unable to load trained SIF model"
            )
            return None

    # =============================================================
    # ML PREDICTION
    # =============================================================

    def _predict_sif_probability(
        self,
        text: str
    ) -> Tuple[float, int]:
        """
        Predict SIF probability using the trained model.

        Returns:
            probability between 0 and 1
            model confidence between 0 and 100
        """

        if self.ml_model is None:
            return 0.0, 0

        try:
            probabilities = self.ml_model.predict_proba([text])[0]
            classes = list(self.ml_model.classes_)

            if "YES" not in classes:
                logger.warning(
                    "YES class not found in trained model"
                )
                return 0.0, 0

            probability = float(
                probabilities[classes.index("YES")]
            )

            confidence = int(
                round(
                    max(
                        probability,
                        1 - probability
                    ) * 100
                )
            )

            return probability, confidence

        except Exception:
            logger.exception(
                "ML prediction failed"
            )
            return 0.0, 0

    # =============================================================
    # MAIN ANALYSIS PIPELINE
    # =============================================================

    def analyze_report(
        self,
        report_text: str
    ) -> AIAnalysisResult:
        """
        Main analysis pipeline.

        Args:
            report_text: Raw safety report text.

        Returns:
            AIAnalysisResult with complete analysis.
        """

        logger.info(
            "Starting report analysis..."
        )

        # ---------------------------------------------------------
        # Step 1: Clean text
        # ---------------------------------------------------------

        cleaned_text = self._clean_text(
            report_text
        )

        logger.debug(
            "Cleaned text: %s...",
            cleaned_text[:100]
        )

        # ---------------------------------------------------------
        # Step 2: ML prediction
        # ---------------------------------------------------------

        ml_probability, ml_confidence = (
            self._predict_sif_probability(
                cleaned_text
            )
        )

        logger.info(
            "Initial ML SIF probability: %s%%",
            round(ml_probability * 100)
        )

        # ---------------------------------------------------------
        # Step 3: Extract evidence
        # ---------------------------------------------------------

        evidence = self._extract_evidence(
            cleaned_text
        )

        logger.info(
            "Extracted %s evidence items",
            len(evidence)
        )

        # ---------------------------------------------------------
        # Step 4: Detect hazards
        # ---------------------------------------------------------

        hazards = self._detect_hazards(
            cleaned_text
        )

        logger.info(
            "Detected hazards: %s",
            hazards
        )

        # ---------------------------------------------------------
        # Step 5: Detect exposure
        # ---------------------------------------------------------

        exposure = self._detect_exposure(
            cleaned_text
        )

        logger.info(
            "Detected exposure: %s",
            exposure
        )

        # ---------------------------------------------------------
        # Step 6: Detect control failures
        # ---------------------------------------------------------

        control_failures = (
            self._detect_control_failures(
                cleaned_text,
                hazards
            )
        )

        logger.info(
            "Detected control failures: %s",
            control_failures
        )

        # ---------------------------------------------------------
        # Step 7: Check low-risk keywords
        # ---------------------------------------------------------

        avoid_found = (
            self._check_avoid_keywords(
                cleaned_text
            )
        )

        if avoid_found:
            logger.info(
                "Low-risk keywords found: %s",
                avoid_found
            )

        # ---------------------------------------------------------
        # Step 8: Detect safety-critical incident
        # ---------------------------------------------------------

        safety_override = (
            self._detect_safety_critical_incident(
                cleaned_text,
                hazards,
                exposure,
                control_failures,
                evidence
            )
        )

        # ---------------------------------------------------------
        # Step 9: Calculate SIF status
        # ---------------------------------------------------------

        sif_status, confidence = (
            self._calculate_sif_status(
                hazards,
                exposure,
                control_failures,
                evidence,
                avoid_found,
                ml_probability
                if self.ml_model is not None
                else None,
                safety_override
            )
        )

        # ---------------------------------------------------------
        # Step 10: Calculate effective SIF probability
        # ---------------------------------------------------------

        sif_probability = (
            self._calculate_effective_probability(
                ml_probability,
                safety_override,
                sif_status,
                confidence
            )
        )

        logger.info(
            "Final SIF Status: %s",
            sif_status
        )

        logger.info(
            "Final SIF Probability: %s%%",
            round(sif_probability * 100)
        )

        logger.info(
            "Final Confidence: %s%%",
            confidence
        )

        # ---------------------------------------------------------
        # Step 11: Calculate risk level
        # ---------------------------------------------------------

        risk_level, risk_score = (
            RiskEngine.calculate_risk_score(
                hazards,
                exposure,
                control_failures,
                evidence,
                sif_probability
            )
        )

        # ---------------------------------------------------------
        # Safety-critical override for risk
        # ---------------------------------------------------------

        if safety_override:
            if risk_level in (
                RiskLevel.LOW,
                RiskLevel.MEDIUM
            ):
                risk_level = RiskLevel.HIGH

                logger.warning(
                    "Safety-critical incident detected. "
                    "Risk elevated to HIGH."
                )

        logger.info(
            "Risk Level: %s (Score: %s)",
            risk_level,
            risk_score
        )

        # ---------------------------------------------------------
        # Step 12: Generate explanation
        # ---------------------------------------------------------

        explanation = (
            self._generate_explanation(
                hazards,
                exposure,
                control_failures,
                evidence,
                sif_status,
                safety_override
            )
        )

        # ---------------------------------------------------------
        # Step 13: Generate recommendations
        # ---------------------------------------------------------

        recommendations_list = (
            RecommendationEngine.generate_recommendations(
                hazards,
                control_failures,
                risk_level
            )
        )

        recommendation = (
            self._format_recommendation(
                recommendations_list,
                risk_level,
                hazards,
                control_failures
            )
        )

        # ---------------------------------------------------------
        # Step 14: Safety action plan
        # ---------------------------------------------------------

        safety_action_plan = (
            self._build_safety_action_plan(
                sif_status,
                risk_level,
                hazards,
                control_failures
            )
        )

        # ---------------------------------------------------------
        # Step 15: Build final result
        # ---------------------------------------------------------

        result = AIAnalysisResult(
            sif_status=sif_status,

            sif_probability=sif_probability,

            confidence=confidence,

            risk_level=risk_level,

            hazards=hazards,

            exposure=exposure,

            control_failures=control_failures,

            evidence=evidence,

            explanation=explanation,

            recommendation=recommendation,

            safety_action_plan=safety_action_plan,

            model_type=(
                ModelType.TFIDF_LOGISTIC
                if self.ml_model is not None
                else ModelType.RULE_ENGINE
            ),

            model_version="1.1"
        )

        logger.info(
            "✓ Analysis complete"
        )

        return result

    # =============================================================
    # SAFETY-CRITICAL INCIDENT DETECTION
    # =============================================================

    def _detect_safety_critical_incident(
        self,
        text: str,
        hazards: List[str],
        exposure: List[str],
        control_failures: List[str],
        evidence: List[str]
    ) -> bool:
        """
        Detect combinations of language that indicate a
        strong safety-critical SIF precursor.

        This is intentionally conservative.

        Example:

        "An electrician was repairing a device while current
        was passing through it and he received a high voltage shock."

        should trigger this rule.
        """

        # ---------------------------------------------------------
        # Person involved
        # ---------------------------------------------------------

        person_present = any(
            keyword in text
            for keyword in [
                "worker",
                "electrician",
                "employee",
                "technician",
                "operator",
                "person",
                "man",
                "maintenance worker",
            ]
        )

        # ---------------------------------------------------------
        # Electrical hazard
        # ---------------------------------------------------------

        electrical_hazard = any(
            keyword in text
            for keyword in [
                "electric",
                "electrical",
                "electricity",
                "current",
                "voltage",
                "high voltage",
                "high-voltage",
                "energized",
                "energised",
                "live equipment",
                "live electrical",
                "live wire",
                "power",
            ]
        )

        # ---------------------------------------------------------
        # Maintenance / repair activity
        # ---------------------------------------------------------

        maintenance_activity = any(
            keyword in text
            for keyword in [
                "repairing",
                "repair",
                "repaired",
                "maintenance",
                "maintaining",
                "maintained",
                "servicing",
                "serviced",
                "service",
                "working on",
                "fixing",
                "installation",
                "installing",
            ]
        )

        # ---------------------------------------------------------
        # Actual electrical exposure / shock
        # ---------------------------------------------------------

        actual_electrical_exposure = any(
            keyword in text
            for keyword in [
                "electric shock",
                "electrical shock",
                "got shocked",
                "got a shock",
                "received a shock",
                "received an electric shock",
                "received an electrical shock",
                "suffered a shock",
                "suffered electric shock",
                "suffered an electric shock",
                "current passed through",
                "current passing through",
                "current flowed through",
                "current flowing through",
                "current was passing",
                "current was flowing",
                "high voltage shock",
                "high-voltage shock",
                "shock of high voltage",
                "high voltage current",
            ]
        )

        # ---------------------------------------------------------
        # Energized condition
        # ---------------------------------------------------------

        energized_condition = any(
            keyword in text
            for keyword in [
                "energized",
                "energised",
                "still energized",
                "still energised",
                "remained energized",
                "remained energised",
                "live equipment",
                "live electrical",
                "working live",
                "working on live",
                "power was on",
                "power remained on",
                "current was passing",
                "current passing",
                "current flowing",
                "current was flowing",
            ]
        )

        # ---------------------------------------------------------
        # Strong combination
        # ---------------------------------------------------------

        strong_electrical_incident = (
            person_present
            and electrical_hazard
            and maintenance_activity
            and actual_electrical_exposure
            and energized_condition
        )

        # ---------------------------------------------------------
        # Slightly broader actual shock rule
        # ---------------------------------------------------------

        actual_shock_with_electrical_hazard = (
            person_present
            and electrical_hazard
            and actual_electrical_exposure
            and (
                maintenance_activity
                or "high voltage" in text
                or "high-voltage" in text
                or "energized" in text
                or "energised" in text
            )
        )

        # ---------------------------------------------------------
        # Strong taxonomy evidence combination
        # ---------------------------------------------------------

        taxonomy_high_risk = (
            len(hazards) > 0
            and len(exposure) > 0
            and len(control_failures) > 0
            and len(evidence) > 0
        )

        if strong_electrical_incident:
            logger.warning(
                "🚨 SAFETY-CRITICAL ELECTRICAL INCIDENT DETECTED"
            )
            return True

        if actual_shock_with_electrical_hazard:
            logger.warning(
                "🚨 ACTUAL ELECTRICAL SHOCK + HAZARD DETECTED"
            )
            return True

        # Do not use the generic taxonomy combination alone as a
        # 90% override. It remains useful for normal classification.

        return False

    # =============================================================
    # EFFECTIVE PROBABILITY
    # =============================================================

    def _calculate_effective_probability(
        self,
        ml_probability: float,
        safety_override: bool,
        sif_status: SIFStatus,
        confidence: int
    ) -> float:
        """
        Combine ML output with deterministic safety rules.

        IMPORTANT:
        A safety-critical rule can raise the displayed SIF
        probability because the rule identifies a high-severity
        pattern that the trained model may under-recognize.

        The probability should be interpreted as an application
        risk score rather than a calibrated statistical probability.
        """

        if safety_override:
            # Strong safety-critical incident.
            #
            # We deliberately keep this below 1.0 rather than
            # pretending the system has absolute certainty.

            safety_probability = 0.90

            # If the ML model is already higher, retain it.
            return max(
                ml_probability,
                safety_probability
            )

        if self.ml_model is not None:
            return max(
                0.0,
                min(
                    1.0,
                    ml_probability
                )
            )

        return self._status_probability(
            sif_status,
            confidence
        )

    # =============================================================
    # SAFETY ACTION PLAN
    # =============================================================

    def _build_safety_action_plan(
        self,
        sif_status: SIFStatus,
        risk_level: RiskLevel,
        hazards: List[str],
        control_failures: List[str],
    ) -> Dict[str, List[str]]:
        """
        Generate conservative actions that never recommend
        unsafe rescue.
        """

        if (
            sif_status == SIFStatus.NO
            and risk_level == RiskLevel.LOW
        ):
            return {
                "Immediate precautions": [
                    "Continue normal controls and document the observation."
                ],

                "Protect others": [
                    "Keep the work area orderly and report any change in conditions."
                ],

                "If someone is in danger": [
                    "Follow the site emergency procedure and notify the supervisor."
                ],

                "Corrective actions": [
                    "No immediate corrective action indicated by the available evidence."
                ],

                "Preventive measures": [
                    "Continue routine inspections and required PPE checks."
                ],
            }

        actions = {
            "Immediate precautions": [
                "Stop or pause the activity if this can be done safely.",
                "Keep unnecessary personnel away from the affected area.",
                "Do not touch, operate, or enter the hazard area unnecessarily.",
                "Notify the responsible supervisor or safety officer.",
            ],

            "Protect others": [
                "Warn nearby workers when it is safe to do so.",
                "Prevent unauthorized entry and establish an appropriate exclusion zone.",
            ],

            "If someone is in danger": [
                "Activate the site's emergency procedure and contact emergency responders.",
                "Do not attempt an untrained rescue or enter the danger zone.",
            ],

            "Corrective actions": [
                "Verify the required critical controls before work resumes.",
                "Review the identified hazard and control failure with the responsible team.",
            ],

            "Preventive measures": [
                "Audit similar tasks and strengthen supervision, training, or engineering controls.",
            ],
        }

        if (
            "HAZARDOUS_ENERGY" in hazards
            or "LOTO/Isolation Failure" in control_failures
        ):
            actions["Corrective actions"].insert(
                0,
                "Apply and verify the site's isolation/LOTO procedure and zero-energy state."
            )

        return actions

    # =============================================================
    # TEXT CLEANING
    # =============================================================

    def _clean_text(
        self,
        text: str
    ) -> str:
        """Clean and normalize report text."""

        if not text:
            return ""

        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        # Keep letters, numbers, spaces and useful punctuation.
        text = re.sub(
            r"[^\w\s.,\-/%]",
            "",
            text
        )

        return text.strip()

    # =============================================================
    # EVIDENCE EXTRACTION
    # =============================================================

    def _extract_evidence(
        self,
        text: str
    ) -> List[str]:
        """Extract key evidence sentences from text."""

        if not text:
            return []

        sentences = re.split(
            r"[.\n]+",
            text
        )

        evidence = []

        keywords = TaxonomyService.get_all_keywords()

        keywords = [
            keyword.lower()
            for keyword in keywords
        ]

        # Additional high-value safety keywords.
        keywords.extend([
            "shock",
            "current",
            "high voltage",
            "high-voltage",
            "energized",
            "energised",
            "live equipment",
            "live electrical",
            "repairing",
            "maintenance",
            "electrician",
        ])

        for sent in sentences:

            sent = sent.strip()

            if len(sent) <= 10:
                continue

            if any(
                keyword in sent
                for keyword in keywords
            ):
                evidence.append(sent)

        # Limit to top 5 evidence items.
        if evidence:
            return evidence[:5]

        return [text[:200]]

    # =============================================================
    # HAZARD DETECTION
    # =============================================================

    def _detect_hazards(
        self,
        text: str
    ) -> List[str]:
        """Detect hazard categories from text."""

        detected_hazards = []

        for category, info in self.categories.items():

            if category in {
                "EXPOSURE",
                "CRITICAL_CONTROL_FAILURE"
            }:
                continue

            keywords = info.get(
                "keywords",
                []
            )

            for keyword in keywords:

                keyword = keyword.lower().strip()

                if (
                    category == "VEHICLE_MOBILE_EQUIPMENT"
                    and keyword in {
                        "equipment",
                        "interaction"
                    }
                ):
                    continue

                if not keyword:
                    continue

                pattern = (
                    r"\b"
                    + re.escape(keyword)
                    + r"\b"
                )

                if (
                    re.search(pattern, text)
                    and not self._is_negated(
                        text,
                        keyword,
                        include_without=False
                    )
                ):
                    if category not in detected_hazards:
                        detected_hazards.append(
                            category
                        )

                    break

        # ---------------------------------------------------------
        # Explicit electrical safety fallback
        # ---------------------------------------------------------

        electrical_keywords = [
            "electric",
            "electrical",
            "electricity",
            "current",
            "voltage",
            "high voltage",
            "high-voltage",
            "energized",
            "energised",
            "live equipment",
            "live electrical",
            "live wire",
            "electric shock",
            "electrical shock",
        ]

        if (
            any(
                keyword in text
                for keyword in electrical_keywords
            )
            and "HAZARDOUS_ENERGY" not in detected_hazards
        ):
            detected_hazards.append(
                "HAZARDOUS_ENERGY"
            )

        return detected_hazards

    # =============================================================
    # EXPOSURE DETECTION
    # =============================================================

    def _detect_exposure(
        self,
        text: str
    ) -> List[str]:
        """
        Detect worker exposure types, including actual
        injury/exposure events.
        """

        exposure_keywords = {

            "Direct Contact": [
                "contact with",
                "came into contact",
                "direct contact",
                "touched",
                "touching",
                "touched the",
                "shock",
                "electric shock",
                "electrical shock",
                "got shocked",
                "got a shock",
                "received a shock",
                "received an electric shock",
                "received an electrical shock",
                "suffered a shock",
                "suffered an electric shock",
                "current passed through",
                "current passing through",
                "current flowed through",
                "current flowing through",
                "current was passing",
                "current was flowing",
                "electrical current through",
                "high voltage shock",
                "high-voltage shock",
                "shock of high voltage",
                "struck",
                "caught",
                "impacted",
            ],

            "Full Exposure": [
                "exposed to",
                "was exposed",
                "directly exposed",
                "entered",
                "inside",
                "in area",
                "working on energized",
                "working on live equipment",
                "working on live electrical",
            ],

            "Partial Exposure": [
                "near",
                "close to",
                "proximity",
                "adjacent",
            ],

            "Proximity": [
                "nearby",
                "in vicinity",
                "alongside",
            ],

            "Repeated Exposure": [
                "repeatedly",
                "frequent",
                "often",
                "regular",
            ],
        }

        detected_exposure = []

        for exposure_type, keywords in exposure_keywords.items():

            for keyword in keywords:

                if keyword in text:

                    if exposure_type not in detected_exposure:
                        detected_exposure.append(
                            exposure_type
                        )

                    break

        # ---------------------------------------------------------
        # Actual electrical shock always means direct exposure.
        # ---------------------------------------------------------

        actual_shock_indicators = [
            "electric shock",
            "electrical shock",
            "got shocked",
            "got a shock",
            "received a shock",
            "received an electric shock",
            "received an electrical shock",
            "suffered a shock",
            "suffered an electric shock",
            "current passed through",
            "current passing through",
            "current flowed through",
            "current flowing through",
            "current was passing",
            "current was flowing",
            "high voltage shock",
            "high-voltage shock",
            "shock of high voltage",
        ]

        if any(
            indicator in text
            for indicator in actual_shock_indicators
        ):
            if "Direct Contact" not in detected_exposure:
                detected_exposure.insert(
                    0,
                    "Direct Contact"
                )

        # ---------------------------------------------------------
        # Worker + actual current/shock
        # ---------------------------------------------------------

        if (
            (
                "worker" in text
                or "electrician" in text
                or "employee" in text
                or "technician" in text
            )
            and any(
                indicator in text
                for indicator in [
                    "shock",
                    "current passed through",
                    "current passing through",
                    "current flowed through",
                    "current flowing through",
                    "current was passing",
                    "current was flowing",
                ]
            )
        ):
            if "Direct Contact" not in detected_exposure:
                detected_exposure.insert(
                    0,
                    "Direct Contact"
                )

        # ---------------------------------------------------------
        # Actual electrical incident = full exposure
        # ---------------------------------------------------------

        if (
            "Direct Contact" in detected_exposure
            and (
                "electric" in text
                or "electrical" in text
                or "current" in text
                or "voltage" in text
            )
        ):
            if "Full Exposure" not in detected_exposure:
                detected_exposure.append(
                    "Full Exposure"
                )

        # ---------------------------------------------------------
        # Only infer proximity when stronger evidence is absent.
        # ---------------------------------------------------------

        if not detected_exposure and (
            "worker" in text
            or "employee" in text
            or "electrician" in text
            or "technician" in text
        ):
            detected_exposure.append(
                "Proximity"
            )

        return detected_exposure

    # =============================================================
    # CONTROL FAILURE DETECTION
    # =============================================================

    def _detect_control_failures(
        self,
        text: str,
        hazards: List[str]
    ) -> List[str]:
        """Detect critical control failures."""

        control_keywords = {

            "LOTO/Isolation Failure": [
                "without isolation",
                "without loto",
                "without lockout",
                "without lock out",
                "not isolated",
                "not properly isolated",
                "isolation failure",
                "failed to isolate",
                "failure to isolate",
                "energized",
                "energised",
                "still energized",
                "still energised",
                "remained energized",
                "remained energised",
                "live equipment",
                "live electrical",
                "working live",
                "working on live",
                "power was on",
                "power remained on",
                "current was passing",
                "current passing",
                "current flowing",
                "current was flowing",
            ],

            "Permit Failure": [
                "without permit",
                "no permit",
                "permit not obtained",
                "unauthorized entry",
            ],

            "PPE Failure": [
                "without ppe",
                "no ppe",
                "no protection",
                "not wearing",
                "without electrical ppe",
                "without protective equipment",
            ],

            "Barrier Bypass": [
                "barrier removed",
                "guard removed",
                "bypass",
                "disabled",
            ],

            "Procedure Violation": [
                "not followed",
                "procedure not",
                "violated procedure",
                "procedure violation",
                "safety procedure not followed",
            ],

            "Lack of Monitoring": [
                "no monitoring",
                "unattended",
                "unsupervised",
            ],
        }

        control_failures = []

        for failure_type, keywords in control_keywords.items():

            for keyword in keywords:

                if keyword in text:

                    if failure_type not in control_failures:
                        control_failures.append(
                            failure_type
                        )

                    break

        # ---------------------------------------------------------
        # Electrical hazard detection
        # ---------------------------------------------------------

        electrical_hazard = any(
            keyword in text
            for keyword in [
                "electric",
                "electrical",
                "electricity",
                "current",
                "voltage",
                "energized",
                "energised",
                "live equipment",
                "live electrical",
            ]
        )

        # ---------------------------------------------------------
        # Actual shock detection
        # ---------------------------------------------------------

        actual_shock = any(
            keyword in text
            for keyword in [
                "electric shock",
                "electrical shock",
                "got shocked",
                "got a shock",
                "received a shock",
                "received an electric shock",
                "received an electrical shock",
                "suffered a shock",
                "suffered an electric shock",
                "current passed through",
                "current passing through",
                "current flowed through",
                "current flowing through",
                "current was passing",
                "current was flowing",
                "high voltage shock",
                "high-voltage shock",
                "shock of high voltage",
            ]
        )

        # ---------------------------------------------------------
        # Maintenance activity
        # ---------------------------------------------------------

        maintenance_activity = any(
            keyword in text
            for keyword in [
                "repairing",
                "repair",
                "repaired",
                "maintenance",
                "maintaining",
                "maintained",
                "servicing",
                "serviced",
                "service",
                "working on",
                "fixing",
            ]
        )

        # ---------------------------------------------------------
        # Energized condition
        # ---------------------------------------------------------

        energized_condition = any(
            keyword in text
            for keyword in [
                "energized",
                "energised",
                "live equipment",
                "live electrical",
                "working live",
                "working on live",
                "current was passing",
                "current passing",
                "current flowing",
                "current was flowing",
                "power was on",
                "power remained on",
            ]
        )

        # ---------------------------------------------------------
        # Maintenance + electricity + shock + energized state
        # ---------------------------------------------------------

        if (
            electrical_hazard
            and maintenance_activity
            and actual_shock
            and energized_condition
        ):

            if "LOTO/Isolation Failure" not in control_failures:

                control_failures.insert(
                    0,
                    "LOTO/Isolation Failure"
                )

        # ---------------------------------------------------------
        # Actual high-voltage shock during repair.
        #
        # Even if the word "energized" is not present, this is
        # strong evidence that energy isolation failed or was
        # inadequate.
        # ---------------------------------------------------------

        high_voltage_incident = (
            electrical_hazard
            and maintenance_activity
            and actual_shock
            and (
                "high voltage" in text
                or "high-voltage" in text
                or "voltage" in text
            )
        )

        if high_voltage_incident:

            if "LOTO/Isolation Failure" not in control_failures:

                control_failures.insert(
                    0,
                    "LOTO/Isolation Failure"
                )

        return control_failures

    # =============================================================
    # LOW-RISK KEYWORD CHECK
    # =============================================================

    def _check_avoid_keywords(
        self,
        text: str
    ) -> List[str]:
        """Check for keywords indicating low risk."""

        found = []

        for keyword in self.avoid_keywords:

            if keyword.lower() in text:
                found.append(
                    keyword
                )

        return found

    # =============================================================
    # SIF STATUS CALCULATION
    # =============================================================

    def _calculate_sif_status(
        self,
        hazards: List[str],
        exposure: List[str],
        control_failures: List[str],
        evidence: List[str],
        avoid_keywords: List[str],
        sif_probability: float = None,
        safety_override: bool = False
    ) -> Tuple[SIFStatus, int]:
        """
        Determine SIF status and confidence.

        Returns:
            Tuple of SIFStatus and confidence 0-100.
        """

        # ---------------------------------------------------------
        # SAFETY OVERRIDE
        # ---------------------------------------------------------

        if safety_override:

            logger.warning(
                "🚨 SIF safety override activated"
            )

            return (
                SIFStatus.YES,
                90
            )

        # ---------------------------------------------------------
        # ML model
        # ---------------------------------------------------------

        if sif_probability is not None:

            if sif_probability >= 0.55:

                return (
                    SIFStatus.YES,
                    int(
                        round(
                            sif_probability * 100
                        )
                    )
                )

            if sif_probability <= 0.45:

                return (
                    SIFStatus.NO,
                    int(
                        round(
                            (1 - sif_probability) * 100
                        )
                    )
                )

            return (
                SIFStatus.UNCERTAIN,
                int(
                    round(
                        max(
                            sif_probability,
                            1 - sif_probability
                        ) * 100
                    )
                )
            )

        # ---------------------------------------------------------
        # Low-risk indicators
        # ---------------------------------------------------------

        if (
            avoid_keywords
            and not control_failures
            and len(hazards) <= 1
        ):
            return (
                SIFStatus.NO,
                90
            )

        # ---------------------------------------------------------
        # No hazards
        # ---------------------------------------------------------

        if not hazards:

            return (
                SIFStatus.NO,
                70
            )

        # ---------------------------------------------------------
        # No exposure
        # ---------------------------------------------------------

        if not exposure:

            return (
                SIFStatus.UNCERTAIN,
                40
            )

        # ---------------------------------------------------------
        # SIF precursor pattern
        # ---------------------------------------------------------

        high_risk_pattern = (
            self._match_precursor_patterns(
                evidence
            )
        )

        if high_risk_pattern:

            if control_failures:

                return (
                    SIFStatus.YES,
                    85
                )

            return (
                SIFStatus.UNCERTAIN,
                70
            )

        # ---------------------------------------------------------
        # Single hazard
        # ---------------------------------------------------------

        if len(hazards) == 1:

            if control_failures:

                return (
                    SIFStatus.YES,
                    75
                )

            return (
                SIFStatus.UNCERTAIN,
                55
            )

        # ---------------------------------------------------------
        # Multiple hazards
        # ---------------------------------------------------------

        if len(hazards) >= 2:

            if control_failures:

                return (
                    SIFStatus.YES,
                    80
                )

            return (
                SIFStatus.UNCERTAIN,
                65
            )

        # ---------------------------------------------------------
        # Default
        # ---------------------------------------------------------

        return (
            SIFStatus.UNCERTAIN,
            50
        )

    # =============================================================
    # STATUS PROBABILITY
    # =============================================================

    def _status_probability(
        self,
        status: SIFStatus,
        confidence: int
    ) -> float:
        """
        Provide a legacy rule-engine value when no trained
        artifact is present.
        """

        if status == SIFStatus.YES:

            return confidence / 100

        if status == SIFStatus.NO:

            return 1 - confidence / 100

        return 0.5

    # =============================================================
    # PRECURSOR PATTERN MATCHING
    # =============================================================

    def _match_precursor_patterns(
        self,
        evidence: List[str]
    ) -> bool:
        """Check if report matches known SIF precursor patterns."""

        combined_text = " ".join(
            evidence
        ).lower()

        for pattern in self.patterns:

            required_keywords = pattern.get(
                "required_keywords",
                []
            )

            if not required_keywords:
                continue

            matches = 0

            for keyword_group in required_keywords:

                alternatives = (
                    keyword_group.split("|")
                )

                if any(
                    alt.strip().lower()
                    in combined_text
                    for alt in alternatives
                ):
                    matches += 1

            if matches == len(
                required_keywords
            ):

                logger.info(
                    "✓ Matched SIF precursor pattern: %s",
                    pattern.get("name")
                )

                return True

        return False

    # =============================================================
    # EXPLANATION GENERATION
    # =============================================================

    def _generate_explanation(
        self,
        hazards: List[str],
        exposure: List[str],
        control_failures: List[str],
        evidence: List[str],
        sif_status: SIFStatus,
        safety_override: bool = False
    ) -> str:
        """Generate explanation of analysis."""

        if safety_override:

            explanation = (
                "HIGH-CONCERN SIF precursor detected. "
                "The report describes an actual worker exposure "
                "to a hazardous energy source during a maintenance "
                "or repair activity. The combination of electrical "
                "energy, direct exposure, and an apparent failure "
                "to establish a verified safe energy state represents "
                "a safety-critical pattern requiring immediate "
                "qualified safety review. "
            )

        elif sif_status == SIFStatus.YES:

            explanation = (
                "Potential SIF precursor detected. "
                "The report describes exposure to a "
                "significant hazard combined with "
                "critical control failure(s). "
            )

        elif sif_status == SIFStatus.UNCERTAIN:

            explanation = (
                "Uncertain SIF status. "
                "The report contains safety concerns "
                "but evidence is incomplete or conflicting. "
            )

        else:

            explanation = (
                "No SIF precursor indicators detected. "
                "Report does not indicate exposure to "
                "high-risk hazards with control failures. "
            )

        if hazards:

            explanation += (
                f"Detected hazards: "
                f"{', '.join(hazards)}. "
            )

        if exposure:

            explanation += (
                f"Worker exposure identified: "
                f"{', '.join(exposure)}. "
            )

        if control_failures:

            explanation += (
                f"Critical control failures: "
                f"{', '.join(control_failures)}. "
            )

        if evidence:

            explanation += (
                f"Key evidence: "
                f"{evidence[0][:150]}..."
            )

        return explanation.strip()

    # =============================================================
    # RECOMMENDATION FORMATTING
    # =============================================================

    def _format_recommendation(
        self,
        recommendations: List[Dict],
        risk_level: RiskLevel,
        hazards: List[str],
        control_failures: List[str]
    ) -> str:
        """Format recommendations into readable text."""

        if not recommendations:

            return (
                RecommendationEngine
                .generate_summary_recommendation(
                    hazards,
                    control_failures,
                    risk_level
                )
            )

        summary = (
            RecommendationEngine
            .generate_summary_recommendation(
                hazards,
                control_failures,
                risk_level
            )
        )

        action = (
            RecommendationEngine
            .get_priority_action(
                risk_level
            )
        )

        return (
            f"{summary}\n\n"
            f"{action}"
        )

    # =============================================================
    # NEGATION DETECTION
    # =============================================================

    def _is_negated(
        self,
        text: str,
        keyword: str,
        include_without: bool = False
    ) -> bool:
        """
        Basic negation detection.

        Prevents statements such as:
        'no electrical hazard'
        from automatically being treated as a positive hazard.
        """

        if not keyword:
            return False

        pattern = re.compile(
            r"\b(?:no|not|without|never|none)\b"
            r".{0,40}"
            + re.escape(keyword),
            re.IGNORECASE
        )

        if pattern.search(text):

            if include_without:
                return True

            return True

        return False


# ================================================================
# GLOBAL AI ENGINE INITIALIZATION
# ================================================================

try:

    ai_engine = AIEngine()

    logger.info(
        "✓ AI Engine initialized"
    )

except Exception as e:

    logger.error(
        "Failed to initialize AI Engine: %s",
        e
    )

    ai_engine = None