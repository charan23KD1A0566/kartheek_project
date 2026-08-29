"""
AI Engine - Main NLP/SIF analysis pipeline
"""

import re
import json
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
    Main AI/NLP Engine for SIF Precursor Analysis

    Pipeline:
    1. Text cleaning and normalization
    2. Hazard detection via taxonomy matching
    3. Exposure detection
    4. Control failure detection
    5. Evidence extraction
    6. Confidence calculation
    7. Risk scoring
    8. Explanation generation
    9. Recommendation generation
    """

    def __init__(self):
        """Initialize AI engine with taxonomy."""

        self.taxonomy = TaxonomyService.load_taxonomy()
        self.categories = TaxonomyService.get_categories()
        self.patterns = TaxonomyService.get_precursor_patterns()
        self.avoid_keywords = TaxonomyService.get_keywords_to_avoid()
        self.ml_model = self._load_ml_model()

    def _load_ml_model(self):
        if joblib is None:
            logger.warning("ML dependencies are unavailable; using taxonomy fallback")
            return None
        model_path = Path(__file__).resolve().parent.parent / "models" / "sif_model.joblib"
        if not model_path.exists():
            logger.warning("Trained model artifact not found: %s", model_path)
            return None
        try:
            model = joblib.load(model_path)
            logger.info("Loaded trained SIF model: %s", model_path)
            return model
        except Exception:
            logger.exception("Unable to load trained SIF model")
            return None

    def _predict_sif_probability(self, text: str) -> Tuple[float, int]:
        if self.ml_model is None:
            return 0.0, 0
        try:
            probabilities = self.ml_model.predict_proba([text])[0]
            classes = list(self.ml_model.classes_)
            probability = float(probabilities[classes.index("YES")])
            confidence = int(round(max(probability, 1 - probability) * 100))
            return probability, confidence
        except Exception:
            logger.exception("ML prediction failed")
            return 0.0, 0

    def analyze_report(self, report_text: str) -> AIAnalysisResult:
        """
        Main analysis pipeline.

        Args:
            report_text: Raw safety report text.

        Returns:
            AIAnalysisResult with complete analysis.
        """

        logger.info("Starting report analysis...")

        # ---------------------------------------------------------
        # Step 1: Clean text
        # ---------------------------------------------------------
        cleaned_text = self._clean_text(report_text)
        sif_probability, model_confidence = self._predict_sif_probability(cleaned_text)

        logger.debug(
            f"Cleaned text: {cleaned_text[:100]}..."
        )

        # ---------------------------------------------------------
        # Step 2: Extract evidence
        # ---------------------------------------------------------
        evidence = self._extract_evidence(cleaned_text)

        logger.info(
            f"Extracted {len(evidence)} evidence items"
        )

        # ---------------------------------------------------------
        # Step 3: Detect hazards
        # ---------------------------------------------------------
        hazards = self._detect_hazards(cleaned_text)

        logger.info(
            f"Detected hazards: {hazards}"
        )

        # ---------------------------------------------------------
        # Step 4: Detect exposure
        # ---------------------------------------------------------
        exposure = self._detect_exposure(cleaned_text)

        logger.info(
            f"Detected exposure: {exposure}"
        )

        # ---------------------------------------------------------
        # Step 5: Detect control failures
        # ---------------------------------------------------------
        control_failures = self._detect_control_failures(
            cleaned_text,
            hazards
        )

        logger.info(
            f"Detected control failures: {control_failures}"
        )

        # ---------------------------------------------------------
        # Step 6: Check low-risk keywords
        # ---------------------------------------------------------
        avoid_found = self._check_avoid_keywords(
            cleaned_text
        )

        if avoid_found:
            logger.info(
                f"Low-risk keywords found: {avoid_found}"
            )

        # ---------------------------------------------------------
        # Step 7: Calculate SIF status and confidence
        # ---------------------------------------------------------
        sif_status, confidence = self._calculate_sif_status(
            hazards,
            exposure,
            control_failures,
            evidence,
            avoid_found,
            sif_probability if self.ml_model is not None else None
        )

        if self.ml_model is not None:
            confidence = model_confidence

        logger.info(
            f"SIF Status: {sif_status} "
            f"(Confidence: {confidence}%)"
        )

        # ---------------------------------------------------------
        # Step 8: Calculate risk level
        # ---------------------------------------------------------
        risk_level, risk_score = RiskEngine.calculate_risk_score(
            hazards,
            exposure,
            control_failures,
            evidence,
            sif_probability if self.ml_model is not None else None
        )

        logger.info(
            f"Risk Level: {risk_level} "
            f"(Score: {risk_score})"
        )

        # ---------------------------------------------------------
        # Step 9: Generate explanation
        # ---------------------------------------------------------
        explanation = self._generate_explanation(
            hazards,
            exposure,
            control_failures,
            evidence,
            sif_status
        )

        # ---------------------------------------------------------
        # Step 10: Generate recommendations
        # ---------------------------------------------------------
        recommendations_list = (
            RecommendationEngine.generate_recommendations(
                hazards,
                control_failures,
                risk_level
            )
        )

        # IMPORTANT:
        # Pass hazards and control_failures because
        # _format_recommendation() expects them.
        recommendation = self._format_recommendation(
            recommendations_list,
            risk_level,
            hazards,
            control_failures
        )
        safety_action_plan = self._build_safety_action_plan(
            sif_status, risk_level, hazards, control_failures
        )

        # ---------------------------------------------------------
        # Build final result
        # ---------------------------------------------------------
        result = AIAnalysisResult(
            sif_status=sif_status,
            sif_probability=sif_probability if self.ml_model is not None else self._status_probability(sif_status, confidence),
            confidence=confidence,
            risk_level=risk_level,
            hazards=hazards,
            exposure=exposure,
            control_failures=control_failures,
            evidence=evidence,
            explanation=explanation,
            recommendation=recommendation,
            safety_action_plan=safety_action_plan,
            model_type=ModelType.TFIDF_LOGISTIC if self.ml_model is not None else ModelType.RULE_ENGINE,
            model_version="1.0"
        )

        logger.info("✓ Analysis complete")

        return result

    def _build_safety_action_plan(
        self,
        sif_status: SIFStatus,
        risk_level: RiskLevel,
        hazards: List[str],
        control_failures: List[str],
    ) -> Dict[str, List[str]]:
        """Generate conservative actions that never recommend unsafe rescue."""
        if sif_status == SIFStatus.NO and risk_level == RiskLevel.LOW:
            return {
                "Immediate precautions": ["Continue normal controls and document the observation."],
                "Protect others": ["Keep the work area orderly and report any change in conditions."],
                "If someone is in danger": ["Follow the site emergency procedure and notify the supervisor."],
                "Corrective actions": ["No immediate corrective action indicated by the available evidence."],
                "Preventive measures": ["Continue routine inspections and required PPE checks."],
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
        if "HAZARDOUS_ENERGY" in hazards or "LOTO/Isolation Failure" in control_failures:
            actions["Corrective actions"].insert(0, "Apply and verify the site's isolation/LOTO procedure and zero-energy state.")
        return actions

    # =============================================================
    # TEXT CLEANING
    # =============================================================

    def _clean_text(self, text: str) -> str:
        """Clean and normalize report text."""

        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters but keep meaningful punctuation
        text = re.sub(
            r"[^\w\s\.\,\-]",
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

        # Split into sentences
        sentences = re.split(
            r"[.\n]",
            text
        )

        evidence = []

        keywords = TaxonomyService.get_all_keywords()

        # Normalize taxonomy keywords
        keywords = [
            keyword.lower()
            for keyword in keywords
        ]

        for sent in sentences:

            sent = sent.strip()

            if len(sent) <= 10:
                continue

            # Check if sentence contains relevant keywords
            if any(
                keyword in sent
                for keyword in keywords
            ):
                evidence.append(sent)

        # Limit to top 5 evidence items
        if evidence:
            return evidence[:5]

        # Fallback evidence
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

            if category in {"EXPOSURE", "CRITICAL_CONTROL_FAILURE"}:
                continue

            keywords = info.get(
                "keywords",
                []
            )

            for keyword in keywords:

                keyword = keyword.lower().strip()

                if category == "VEHICLE_MOBILE_EQUIPMENT" and keyword in {"equipment", "interaction"}:
                    continue

                if not keyword:
                    continue

                # Use word boundaries
                pattern = (
                    r"\b"
                    + re.escape(keyword)
                    + r"\b"
                )

                if re.search(pattern, text) and not self._is_negated(text, keyword, include_without=False):

                    if category not in detected_hazards:
                        detected_hazards.append(
                            category
                        )

                    break

        return detected_hazards

    # =============================================================
    # EXPOSURE DETECTION
    # =============================================================

    def _detect_exposure(
        self,
        text: str
    ) -> List[str]:
        """Detect worker exposure types."""

        exposure_keywords = {

            "Direct Contact": [
                "contact with",
                "touched",
                "struck",
                "caught",
                "impacted"
            ],

            "Full Exposure": [
                "exposed to",
                "inside",
                "in close contact"
            ],

            "Partial Exposure": [
                "near",
                "close to",
                "proximity",
                "adjacent"
            ],

            "Proximity": [
                "nearby",
                "in vicinity",
                "alongside"
            ],

            "Repeated Exposure": [
                "repeatedly",
                "frequent",
                "often",
                "regular"
            ]
        }

        detected_exposure = []

        for exposure_type, keywords in exposure_keywords.items():

            for keyword in keywords:

                if keyword in text and not self._is_negated(text, keyword):

                    if exposure_type not in detected_exposure:
                        detected_exposure.append(
                            exposure_type
                        )

                    break

        # If worker is mentioned but
        # no specific exposure was detected
        if (
            not detected_exposure
            and (
                "worker" in text
                or "employee" in text
            )
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

        control_failures = []

        control_keywords = {

            "LOTO/Isolation Failure": [
                "without isolation",
                "without loto",
                "without lockout",
                "not isolated",
                "energized"
            ],

            "Permit Failure": [
                "without permit",
                "no permit",
                "unauthorized entry"
            ],

            "PPE Failure": [
                "without ppe",
                "without a safety harness",
                "without safety harness",
                "no protection",
                "no harness",
                "not wearing"
            ],

            "Barrier Bypass": [
                "barrier removed",
                "guard removed",
                "bypass",
                "disabled"
            ],

            "Procedure Violation": [
                "not followed",
                "procedure not",
                "violated procedure"
            ],

            "Lack of Monitoring": [
                "no monitoring",
                "no gas monitoring",
                "no atmospheric testing",
                "without atmospheric testing",
                "without a gas monitor",
                "without gas monitoring",
                "unattended",
                "unsupervised"
            ]
        }

        for failure_type, keywords in control_keywords.items():

            for keyword in keywords:

                if keyword in text and not self._is_negated(text, keyword, include_without=False):

                    if failure_type not in control_failures:
                        control_failures.append(
                            failure_type
                        )

                    break

        return control_failures

    def _is_negated(self, text: str, phrase: str, include_without: bool = True) -> bool:
        """Detect simple negation immediately before a matched phrase."""

        negations = "no|not|never|without" if include_without else "no|not|never"
        negation_pattern = (
            rf"\b(?:{negations})\b(?:\W+\w+){{0,4}}\W+"
            + re.escape(phrase)
            + r"\b"
        )
        return re.search(negation_pattern, text) is not None

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
                found.append(keyword)

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
        sif_probability: float = None
    ) -> Tuple[SIFStatus, int]:
        """
        Determine SIF status and confidence.

        Returns:
            Tuple of SIFStatus and confidence 0-100.
        """

        if sif_probability is not None:
            if sif_probability >= 0.55:
                return SIFStatus.YES, int(round(sif_probability * 100))
            if sif_probability <= 0.45:
                return SIFStatus.NO, int(round((1 - sif_probability) * 100))
            return SIFStatus.UNCERTAIN, int(round(max(sif_probability, 1 - sif_probability) * 100))

        # ---------------------------------------------------------
        # Low-risk indicators
        # ---------------------------------------------------------
        if (
            avoid_keywords
            and not control_failures
            and len(hazards) <= 1
        ):
            return SIFStatus.NO, 90

        # ---------------------------------------------------------
        # No hazards
        # ---------------------------------------------------------
        if not hazards:
            return SIFStatus.NO, 70

        # ---------------------------------------------------------
        # No exposure
        # ---------------------------------------------------------
        if not exposure:
            return SIFStatus.UNCERTAIN, 40

        # ---------------------------------------------------------
        # Check SIF precursor patterns
        # ---------------------------------------------------------
        high_risk_pattern = (
            self._match_precursor_patterns(
                evidence
            )
        )

        if high_risk_pattern:

            if control_failures:
                return SIFStatus.YES, 85

            return SIFStatus.UNCERTAIN, 70

        # ---------------------------------------------------------
        # Single hazard
        # ---------------------------------------------------------
        if len(hazards) == 1:

            if control_failures:
                return SIFStatus.YES, 75

            return SIFStatus.UNCERTAIN, 55

        # ---------------------------------------------------------
        # Multiple hazards
        # ---------------------------------------------------------
        if len(hazards) >= 2:

            if control_failures:
                return SIFStatus.YES, 80

            return SIFStatus.UNCERTAIN, 65

        # ---------------------------------------------------------
        # Default
        # ---------------------------------------------------------
        return SIFStatus.UNCERTAIN, 50

    def _status_probability(self, status: SIFStatus, confidence: int) -> float:
        """Provide an honest legacy value when no trained artifact is present."""
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

            # If pattern has no required keywords,
            # don't consider it a match.
            if not required_keywords:
                continue

            matches = 0

            for keyword_group in required_keywords:

                alternatives = keyword_group.split("|")

                if any(
                    alt.strip().lower()
                    in combined_text
                    for alt in alternatives
                ):
                    matches += 1

            # All keyword groups must match
            if matches == len(
                required_keywords
            ):

                logger.info(
                    "✓ Matched SIF precursor pattern: "
                    f"{pattern.get('name')}"
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
        sif_status: SIFStatus
    ) -> str:
        """Generate explanation of analysis."""

        if sif_status == SIFStatus.YES:

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
                f"{evidence[0][:100]}..."
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

        # ---------------------------------------------------------
        # No specific recommendations
        # ---------------------------------------------------------
        if not recommendations:

            return (
                RecommendationEngine
                .generate_summary_recommendation(
                    hazards,
                    control_failures,
                    risk_level
                )
            )

        # ---------------------------------------------------------
        # Generate summary using ACTUAL detected hazards
        # and ACTUAL detected control failures.
        # ---------------------------------------------------------
        summary = (
            RecommendationEngine
            .generate_summary_recommendation(
                hazards,
                control_failures,
                risk_level
            )
        )

        # ---------------------------------------------------------
        # Add top priority action
        # ---------------------------------------------------------
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
        f"Failed to initialize AI Engine: {e}"
    )

    ai_engine = None