"""
Taxonomy service - Load and manage SIF taxonomy
"""

import json
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "../../data/taxonomy.json")


class TaxonomyService:
    """Manage SIF taxonomy"""
    
    _taxonomy: Optional[Dict] = None
    
    @classmethod
    def load_taxonomy(cls) -> Dict:
        """Load taxonomy from JSON file"""
        if cls._taxonomy:
            return cls._taxonomy
        
        try:
            with open(TAXONOMY_PATH, 'r') as f:
                cls._taxonomy = json.load(f)
            logger.info("✓ Taxonomy loaded successfully")
            return cls._taxonomy
        except FileNotFoundError:
            logger.error(f"Taxonomy file not found: {TAXONOMY_PATH}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid taxonomy JSON: {e}")
            raise
    
    @classmethod
    def get_categories(cls) -> Dict:
        """Get all taxonomy categories"""
        taxonomy = cls.load_taxonomy()
        return taxonomy.get("categories", {})
    
    @classmethod
    def get_category_keywords(cls, category: str) -> List[str]:
        """Get keywords for a specific category"""
        categories = cls.get_categories()
        return categories.get(category, {}).get("keywords", [])
    
    @classmethod
    def get_all_keywords(cls) -> List[str]:
        """Get all keywords from taxonomy"""
        keywords = []
        for category in cls.get_categories().values():
            keywords.extend(category.get("keywords", []))
        return keywords
    
    @classmethod
    def get_precursor_patterns(cls) -> List[Dict]:
        """Get SIF precursor patterns"""
        taxonomy = cls.load_taxonomy()
        return taxonomy.get("precursor_patterns", [])
    
    @classmethod
    def get_category_info(cls, category: str) -> Optional[Dict]:
        """Get full info for a category"""
        categories = cls.get_categories()
        return categories.get(category)
    
    @classmethod
    def get_category_weight(cls, category: str) -> float:
        """Get risk weight for a category"""
        info = cls.get_category_info(category)
        return info.get("risk_weight", 0.5) if info else 0.5
    
    @classmethod
    def get_category_controls(cls, category: str) -> List[str]:
        """Get recommended controls for a category"""
        info = cls.get_category_info(category)
        return info.get("control_examples", []) if info else []
    
    @classmethod
    def get_keywords_to_avoid(cls) -> List[str]:
        """Get keywords that suggest low risk"""
        taxonomy = cls.load_taxonomy()
        return taxonomy.get("keywords_to_avoid", [])
    
    @classmethod
    def category_exists(cls, category: str) -> bool:
        """Check if category exists"""
        categories = cls.get_categories()
        return category in categories


# Initialize taxonomy on module import
try:
    TaxonomyService.load_taxonomy()
except Exception as e:
    logger.error(f"Failed to load taxonomy: {e}")
