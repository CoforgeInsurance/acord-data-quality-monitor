"""
AI-GENERATED ACORD Parser from YAML Contracts

This file is AUTO-GENERATED from:
- contracts/submission_quality_rules.yml
- contracts/dim_submission.yml

DO NOT EDIT MANUALLY - Regenerate using AI from contract specifications
"""

from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import uuid
import xml.etree.ElementTree as ET

from src.models.submission import ACORDSubmission
from src.utils.contract_loader import ContractLoader


class ACORDParser:
    """
    Parse ACORD 103 XML submissions based on YAML contracts.
    
    AI-GENERATED from contracts to extract fields defined in:
    - dim_submission.yml (schema mappings)
    - submission_quality_rules.yml (field definitions)
    """
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """
        Initialize ACORD parser with contract loader.
        
        Args:
            contracts_dir: Path to contracts directory
        """
        self.contract_loader = ContractLoader(contracts_dir)
        self.dim_submission_contract = self.contract_loader.get_dim_submission_contract()
        self.quality_rules_contract = self.contract_loader.get_quality_rules_contract()
    
    def parse_xml(self, xml_file: Path) -> ACORDSubmission:
        """
        Parse ACORD 103 XML file and return structured submission.
        
        Args:
            xml_file: Path to ACORD XML file
        
        Returns:
            ACORDSubmission Pydantic model
        
        Raises:
            FileNotFoundError: If XML file doesn't exist
            ET.ParseError: If XML is malformed
            ValueError: If required fields are missing
        """
        if not xml_file.exists():
            raise FileNotFoundError(f"XML file not found: {xml_file}")
        
        # Parse XML
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Extract fields based on contract mappings
        extracted_data = {}
        
        # Generate submission_id if not present
        extracted_data['submission_id'] = str(uuid.uuid4())
        
        # Extract ACORD submission number
        extracted_data['acord_submission_number'] = self._extract_field(
            root, "CommercialSubmission/SubmissionNumber"
        )
        
        # Extract business name (required)
        extracted_data['business_name'] = self._extract_field(
            root, "CommercialSubmission/Applicant/BusinessInfo/BusinessName", required=True
        )
        
        # Extract NAICS code (required)
        extracted_data['naics_code'] = self._extract_field(
            root, "CommercialSubmission/Applicant/BusinessInfo/NAICSCode", required=True
        )
        
        # Extract annual revenue (required)
        revenue_str = self._extract_field(
            root, "CommercialSubmission/Applicant/FinancialInfo/AnnualRevenue", required=True
        )
        extracted_data['annual_revenue'] = Decimal(revenue_str)
        
        # Extract employee count (required)
        employee_str = self._extract_field(
            root, "CommercialSubmission/Applicant/EmployeeInfo/TotalEmployees", required=True
        )
        extracted_data['employee_count'] = int(employee_str)
        
        # Extract years in business (required)
        years_str = self._extract_field(
            root, "CommercialSubmission/Applicant/BusinessInfo/YearsInBusiness", required=True
        )
        extracted_data['years_in_business'] = int(years_str)
        
        # Extract business address (required) - combine address fields
        address_parts = []
        street = self._extract_field(root, "CommercialSubmission/Applicant/Address/Street")
        city = self._extract_field(root, "CommercialSubmission/Applicant/Address/City")
        state = self._extract_field(root, "CommercialSubmission/Applicant/Address/State")
        postal = self._extract_field(root, "CommercialSubmission/Applicant/Address/PostalCode")
        
        if street:
            address_parts.append(street)
        if city:
            address_parts.append(city)
        if state:
            address_parts.append(state)
        if postal:
            address_parts.append(postal)
        
        if not address_parts:
            raise ValueError("Business address is required but not found in XML")
        
        extracted_data['business_address'] = ", ".join(address_parts)
        
        # Extract coverage types (required)
        extracted_data['requested_coverage_types'] = self._extract_field(
            root, "CommercialSubmission/CoverageRequest/CoverageType", required=True
        )
        
        # Extract coverage limits (required)
        extracted_data['requested_limits'] = self._extract_field(
            root, "CommercialSubmission/CoverageRequest/Limits", required=True
        )
        
        # Extract submission date (required)
        submission_date_str = self._extract_field(
            root, "CommercialSubmission/SubmissionDate", required=True
        )
        extracted_data['submission_date'] = self._parse_datetime(submission_date_str)
        
        # Set created_at to now
        extracted_data['created_at'] = datetime.now()
        
        # Create and validate Pydantic model
        return ACORDSubmission(**extracted_data)
    
    def _extract_field(
        self,
        root: ET.Element,
        xpath: str,
        required: bool = False
    ) -> Optional[str]:
        """
        Extract field value from XML using simplified XPath.
        
        Args:
            root: XML root element
            xpath: Simplified XPath (e.g., "CommercialSubmission/Applicant/BusinessInfo/BusinessName")
            required: Whether field is required
        
        Returns:
            Field value as string or None if not found
        
        Raises:
            ValueError: If required field is missing
        """
        # Split xpath into parts
        parts = xpath.split('/')
        
        # Navigate XML tree
        current = root
        for part in parts:
            # Find child element (ignore namespaces for simplicity)
            found = None
            for child in current:
                # Strip namespace from tag
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if tag == part:
                    found = child
                    break
            
            if found is None:
                if required:
                    raise ValueError(f"Required field not found: {xpath}")
                return None
            
            current = found
        
        # Return text content
        text = current.text
        if required and not text:
            raise ValueError(f"Required field is empty: {xpath}")
        
        return text.strip() if text else None
    
    def _parse_datetime(self, date_str: str) -> datetime:
        """
        Parse datetime string from XML.
        
        Supports ISO format and common date formats.
        
        Args:
            date_str: Date/time string
        
        Returns:
            Parsed datetime
        
        Raises:
            ValueError: If date format is not recognized
        """
        # Try ISO format first
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # Try common formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y',
            '%d/%m/%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse datetime: {date_str}")
    
    def parse_multiple(self, xml_files: list[Path]) -> list[ACORDSubmission]:
        """
        Parse multiple ACORD XML files.
        
        Args:
            xml_files: List of XML file paths
        
        Returns:
            List of ACORDSubmission models
        """
        submissions = []
        for xml_file in xml_files:
            try:
                submission = self.parse_xml(xml_file)
                submissions.append(submission)
            except Exception as e:
                print(f"Error parsing {xml_file}: {e}")
        
        return submissions
