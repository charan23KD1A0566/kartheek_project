"""
Risk scoring engine - Calculate risk levels
"""

from typing import List, Dict, Tuple
from models import RiskLevel
from config import RISK_ENGINE_CONFIG
import logging

logger = logging.getLogger(__name__)


class RiskEngine:
    """
    Prototype Risk Scoring Engine
    
    Calculates risk based on:
    1. Hazard severity (weight: 0.35)
    2. Worker exposure (weight: 0.25)
    3. Critical control failure (weight: 0.30)
    4. Consequence potential (weight: 0.10)
    
    This is a PROTOTYPE methodology for hackathon demonstration.
    Production systems should use verified OIL risk assessment methods.
    """
    
    # Hazard severity scores
    HAZARD_SEVERITY_SCORES = {
        "HAZARDOUS_ENERGY": 0.9,
        "CONFINED_SPACE": 0.95,
        "LINE_OF_FIRE": 0.85,
        "WORKING_AT_HEIGHT": 0.85,
        "VEHICLE_MOBILE_EQUIPMENT": 0.80,
        "CRITICAL_CONTROL_FAILURE": 0.75,
        "EXPOSURE": 0.50,
    }
    
    # Exposure severity scores
    EXPOSURE_SEVERITY_SCORES = {
        "Direct Contact": 1.0,
        "Full Exposure": 0.95,
        "Partial Exposure": 0.70,
        "Proximity": 0.50,
        "Repeated Exposure": 0.85,
    }
    
    # Control failure severity scores
    CONTROL_FAILURE_SEVERITY_SCORES = {
        "LOTO/Isolation Failure": 0.95,
        "Permit Failure": 0.90,
        "PPE Failure": 0.80,
        "Barrier Bypass": 0.85,
        "Procedure Violation": 0.70,
        "Lack of Monitoring": 0.80,
    }
    
    # Consequence potential keywords
    CONSEQUENCE_KEYWORDS = {
        "fatal": 1.0,
        "death": 1.0,
        "amputation": 0.95,
        "permanent disability": 0.90,
        "severe injury": 0.85,
        "hospitalization": 0.80,
        "loss of eye": 0.95,
        "severe": 0.75,
    }
    
    @classmethod
    def calculate_risk_score(
        cls,
        hazards: List[str],
        exposure: List[str],
        control_failures: List[str],
        evidence: List[str],
        sif_probability: float = None,
    ) -> Tuple[RiskLevel, float]:
        """
        Calculate risk level and score (0-100)
        
        Args:
            hazards: List of detected hazard categories
            exposure: List of detected exposures
            control_failures: List of control failures
            evidence: List of evidence strings from report
        
        Returns:
            Tuple of (RiskLevel, confidence_score 0-100)
        """
        
        # Calculate component scores
        hazard_score = cls._calculate_hazard_score(hazards)
        exposure_score = cls._calculate_exposure_score(exposure)
        control_score = cls._calculate_control_score(control_failures)
        consequence_score = cls._calculate_consequence_score(evidence)
        
        logger.debug(f"Risk components - Hazard: {hazard_score:.2f}, Exposure: {exposure_score:.2f}, "
                    f"Control: {control_score:.2f}, Consequence: {consequence_score:.2f}")
        
        # Apply weights
        weights = RISK_ENGINE_CONFIG
        overall_score = (
            hazard_score * weights["hazard_severity_weight"] +
            exposure_score * weights["exposure_weight"] +
            control_score * weights["control_failure_weight"] +
            consequence_score * weights["consequence_potential_weight"]
        )

        if sif_probability is not None:
            overall_score = overall_score * 0.7 + sif_probability * 0.3
        
        # Normalize to 0-100
        overall_score = min(100, max(0, overall_score * 100))
        
        # Map to risk level
        risk_level = cls._score_to_risk_level(overall_score)
        
        logger.info(f"Risk Score: {overall_score:.1f} -> {risk_level}")
        
        return risk_level, int(overall_score)
    
    @classmethod
    def _calculate_hazard_score(cls, hazards: List[str]) -> float:
        """Calculate hazard severity score"""
        if not hazards:
            return 0.0
        
        scores = []
        for hazard in hazards:
            score = cls.HAZARD_SEVERITY_SCORES.get(hazard, 0.5)
            scores.append(score)
        
        # Use maximum hazard score (worst case)
        return max(scores) if scores else 0.0
    
    @classmethod
    def _calculate_exposure_score(cls, exposure: List[str]) -> float:
        """Calculate worker exposure score"""
        if not exposure:
            return 0.3  # Default if no specific exposure detected
        
        scores = []
        for exp in exposure:
            score = cls.EXPOSURE_SEVERITY_SCORES.get(exp, 0.5)
            scores.append(score)
        
        # Use average of exposures
        return sum(scores) / len(scores) if scores else 0.5
    
    @classmethod
    def _calculate_control_score(cls, control_failures: List[str]) -> float:
        """Calculate control failure severity score"""
        if not control_failures:
            return 0.2  # Low score if controls seem intact
        
        scores = []
        for control in control_failures:
            score = cls.CONTROL_FAILURE_SEVERITY_SCORES.get(control, 0.5)
            scores.append(score)
        
        # Use maximum control failure (worst case)
        return max(scores) if scores else 0.0
    
    @classmethod
    def _calculate_consequence_score(cls, evidence: List[str]) -> float:
        """Calculate consequence potential from evidence"""
        if not evidence:
            return 0.2
        
        combined_text = " ".join(evidence).lower()
        
        scores = []
        for keyword, score in cls.CONSEQUENCE_KEYWORDS.items():
            if keyword in combined_text:
                scores.append(score)
        
        # Use maximum consequence keyword found
        return max(scores) if scores else 0.2
    
    @classmethod
    def _score_to_risk_level(cls, score: float) -> RiskLevel:
        """Map numerical score to risk level"""
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    @classmethod
    def get_methodology_description(cls) -> str:
        """Get description of risk methodology"""
        return """
PROTOTYPE RISK PRIORITIZATION METHODOLOGY

This is a demonstration risk-scoring system for hackathon evaluation.

Components:
1. Hazard Severity (35%) - Type and intensity of energy/hazard
2. Worker Exposure (25%) - Degree of worker proximity/contact
3. Control Failure (30%) - Severity of safety control gaps
4. Consequence Potential (10%) - Evidence of injury severity in report

Scoring:
- Each component scored 0-1.0
- Weighted sum normalized to 0-100
- Mapped to Risk Levels:
  * 80-100: CRITICAL
  * 60-79: HIGH
  * 40-59: MEDIUM
  * 0-39: LOW

IMPORTANT: This is NOT an official OIL risk methodology.
Production systems must use verified, domain-specific assessment methods.
        """
