"""
Mock External APIs for Demo

Simulates OpenCorporates and NAICS lookup APIs
without requiring real API keys or network calls.
"""

from typing import Dict, Optional, Any
import asyncio
import random


class MockOpenCorporatesAPI:
    """Mock OpenCorporates API for business data enrichment"""
    
    SAMPLE_DATA = {
        "541511": {"industry": "Custom Computer Programming Services", "risk": "low"},
        "722511": {"industry": "Full-Service Restaurants", "risk": "medium"},
        "238210": {"industry": "Electrical Contractors", "risk": "high"},
    }
    
    async def search_company(self, business_name: str, state: str = None) -> Optional[Dict[str, Any]]:
        """
        Mock company search.
        
        Args:
            business_name: Business name to search
            state: State code (optional)
            
        Returns:
            Mock company data or None
        """
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        # 80% success rate for demo
        if random.random() < 0.8:
            return {
                "company_name": business_name,
                "jurisdiction": state or "DE",
                "status": "Active",
                "incorporation_date": "2015-01-01",
                "confidence": 0.9
            }
        return None


class MockNAICSLookupAPI:
    """Mock NAICS Lookup API for industry classification"""
    
    NAICS_DATA = {
        "541511": {
            "code": "541511",
            "title": "Custom Computer Programming Services",
            "sector": "Professional, Scientific, and Technical Services",
            "risk_classification": "low",
            "confidence": 0.95
        },
        "722511": {
            "code": "722511",
            "title": "Full-Service Restaurants",
            "sector": "Accommodation and Food Services",
            "risk_classification": "medium",
            "confidence": 0.95
        },
        "238210": {
            "code": "238210",
            "title": "Electrical Contractors and Other Wiring Installation Contractors",
            "sector": "Construction",
            "risk_classification": "high",
            "confidence": 0.95
        }
    }
    
    async def validate_naics(self, naics_code: str) -> Optional[Dict[str, Any]]:
        """
        Mock NAICS code validation.
        
        Args:
            naics_code: 6-digit NAICS code
            
        Returns:
            Mock NAICS data or None
        """
        # Simulate API delay
        await asyncio.sleep(0.05)
        
        return self.NAICS_DATA.get(naics_code)
    
    async def infer_naics_from_business_name(self, business_name: str) -> Optional[Dict[str, Any]]:
        """
        Mock NAICS code inference from business name.
        
        Args:
            business_name: Business name
            
        Returns:
            Mock NAICS data with lower confidence
        """
        await asyncio.sleep(0.1)
        
        # Simple keyword matching for demo
        name_lower = business_name.lower()
        
        if "tech" in name_lower or "software" in name_lower or "computer" in name_lower:
            data = self.NAICS_DATA["541511"].copy()
            data["confidence"] = 0.75  # Lower confidence for inference
            return data
        elif "restaurant" in name_lower or "cafe" in name_lower or "diner" in name_lower:
            data = self.NAICS_DATA["722511"].copy()
            data["confidence"] = 0.75
            return data
        elif "electric" in name_lower or "contractor" in name_lower:
            data = self.NAICS_DATA["238210"].copy()
            data["confidence"] = 0.75
            return data
        
        return None
