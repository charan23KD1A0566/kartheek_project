"""
Recommendation engine - Generate safety review recommendations
"""

from typing import List, Dict
from models import RiskLevel
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generate practical safety review recommendations"""
    
    RECOMMENDATIONS = {
        "HAZARDOUS_ENERGY": {
            "title": "Hazardous Energy - Isolation/LOTO",
            "recommendations": [
                "Verify all energy isolation procedures (LOTO/Tagout) are properly documented and followed.",
                "Confirm workers have completed hazardous-energy training.",
                "Review equipment de-energization procedures before maintenance continues.",
                "Ensure energy-source verification is completed before work proceeds.",
                "Audit LOTO compliance for similar equipment in the facility.",
            ],
            "priority": "CRITICAL"
        },
        "WORKING_AT_HEIGHT": {
            "title": "Working at Height - Fall Protection",
            "recommendations": [
                "Review fall-protection system design and installation.",
                "Verify fall-protection use and compliance before work continues.",
                "Confirm scaffold inspection and certification are current.",
                "Conduct training review on proper harness use and attachment.",
                "Inspect guardrails, safety nets, or other controls for integrity.",
                "Evaluate alternatives for working at height where feasible.",
            ],
            "priority": "CRITICAL"
        },
        "LINE_OF_FIRE": {
            "title": "Line of Fire - Hazard Isolation",
            "recommendations": [
                "Review load securing and suspension controls.",
                "Verify suspended load certification and inspection.",
                "Confirm pedestrian exclusion zones are clearly marked and enforced.",
                "Evaluate mobile-equipment spotters and communication systems.",
                "Review load path and identify pinch points for workers.",
                "Implement barriers to prevent unauthorized entry into work zones.",
            ],
            "priority": "CRITICAL"
        },
        "CONFINED_SPACE": {
            "title": "Confined Space - Entry & Rescue Procedures",
            "recommendations": [
                "Verify confined-space entry permits are completed and properly authorized.",
                "Confirm atmospheric testing was performed and documented.",
                "Review rescue procedures and equipment availability.",
                "Ensure trained monitors were present during entry.",
                "Verify adequate ventilation and hazard controls.",
                "Conduct atmosphere re-testing at appropriate intervals.",
                "Review communication systems for entry team and rescue personnel.",
            ],
            "priority": "CRITICAL"
        },
        "VEHICLE_MOBILE_EQUIPMENT": {
            "title": "Vehicle & Mobile Equipment - Pedestrian Safety",
            "recommendations": [
                "Review pedestrian segregation controls and barriers.",
                "Verify reversing alarms and warning systems are functional.",
                "Confirm operator training and certification are current.",
                "Establish and enforce speed limits in work areas.",
                "Evaluate blind-spot visibility and address with mirrors/cameras.",
                "Implement spotter procedures for high-risk operations.",
                "Conduct near-miss/incident review with equipment operator.",
            ],
            "priority": "HIGH"
        },
        "CRITICAL_CONTROL_FAILURE": {
            "title": "Control Failure - Safety System Review",
            "recommendations": [
                "Identify which critical safety controls failed or were bypassed.",
                "Review the reason for control failure or bypass.",
                "Confirm proper control restoration before work continues.",
                "Audit similar equipment/processes for similar failures.",
                "Enhance control reliability through engineering or administrative changes.",
                "Provide targeted refresher training on control usage.",
                "Implement verification/audit procedures to prevent recurrence.",
            ],
            "priority": "HIGH"
        },
        "EXPOSURE": {
            "title": "Worker Exposure - Distance & Isolation",
            "recommendations": [
                "Evaluate whether worker distance from hazard can be increased.",
                "Review process design to minimize exposure time.",
                "Implement administrative controls to reduce exposure frequency.",
                "Provide additional personal protective equipment if needed.",
                "Enhance awareness and training on exposure risks.",
                "Consider engineering controls to eliminate hazard at source.",
            ],
            "priority": "MEDIUM"
        },
    }
    
    @classmethod
    def generate_recommendations(
        cls,
        hazards: List[str],
        control_failures: List[str],
        risk_level: RiskLevel,
    ) -> List[Dict]:
        """
        Generate recommendations based on detected issues
        
        Args:
            hazards: List of detected hazard categories
            control_failures: List of control failures
            risk_level: Overall risk level
        
        Returns:
            List of recommendation dictionaries
        """
        
        recommendations = []
        
        # Generate recommendations for each hazard
        for hazard in hazards:
            if hazard in cls.RECOMMENDATIONS:
                rec_data = cls.RECOMMENDATIONS[hazard]
                recommendations.append({
                    "category": hazard,
                    "title": rec_data["title"],
                    "actions": rec_data["recommendations"],
                    "priority": rec_data["priority"],
                    "risk_context": risk_level
                })
        
        # Add control-specific recommendations
        for control in control_failures:
            if control in cls.RECOMMENDATIONS:
                rec_data = cls.RECOMMENDATIONS[control]
                recommendations.append({
                    "category": control,
                    "title": rec_data["title"],
                    "actions": rec_data["recommendations"],
                    "priority": rec_data["priority"],
                    "risk_context": risk_level
                })
        
        # Remove duplicates based on category
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec["category"] not in seen:
                seen.add(rec["category"])
                unique_recs.append(rec)
        
        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        unique_recs.sort(
            key=lambda x: priority_order.get(x["priority"], 999)
        )
        
        logger.info(f"Generated {len(unique_recs)} unique recommendations")
        
        return unique_recs
    
    @classmethod
    def generate_summary_recommendation(
        cls,
        hazards: List[str],
        control_failures: List[str],
        risk_level: RiskLevel,
    ) -> str:
        """
        Generate a concise summary recommendation
        """
        
        if risk_level == RiskLevel.CRITICAL:
            summary = "⚠️ CRITICAL - This report indicates potential exposure to serious injury/fatality. "
            summary += "Recommend immediate safety-professional review and work suspension if active."
        elif risk_level == RiskLevel.HIGH:
            summary = "⚠️ HIGH RISK - This report indicates significant safety concerns. "
            summary += "Recommend prompt safety-professional review before work continues."
        elif risk_level == RiskLevel.MEDIUM:
            summary = "⚠ MEDIUM RISK - This report indicates notable safety issues. "
            summary += "Recommend standard safety review and corrective action planning."
        else:
            summary = "✓ LOW RISK - This report does not appear to indicate immediate SIF precursors. "
            summary += "Standard observation and documentation recommended."
        
        if hazards:
            summary += f" Key hazards: {', '.join(hazards[:3])}."
        
        if control_failures:
            summary += f" Control failures: {', '.join(control_failures[:2])}."
        
        return summary
    
    @classmethod
    def get_priority_action(cls, risk_level: RiskLevel) -> str:
        """Get immediate action for risk level"""
        actions = {
            RiskLevel.CRITICAL: "🛑 STOP WORK & IMMEDIATE REVIEW - Contact safety professional immediately",
            RiskLevel.HIGH: "⚠️ SUSPEND SIMILAR ACTIVITIES - Conduct safety review within hours",
            RiskLevel.MEDIUM: "🔍 REVIEW & INVESTIGATE - Assess within 24-48 hours",
            RiskLevel.LOW: "📋 DOCUMENT & MONITOR - Standard documentation and trending",
        }
        return actions.get(risk_level, "Review required")
