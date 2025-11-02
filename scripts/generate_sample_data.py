"""
Generate synthetic ACORD 103 XML submission files for testing.

This script creates realistic insurance submissions with varying quality:
- Complete submissions (100% fields populated, all validations pass)
- Incomplete submissions (missing required fields)
- Anomalous submissions (data quality issues, consistency violations)
"""

import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring, Comment
from xml.dom import minidom


# Sample business data
BUSINESS_NAMES = [
    "Acme Software Solutions LLC",
    "Global Manufacturing Corp",
    "Premier Healthcare Associates",
    "TechStart Innovations Inc",
    "Riverside Construction Co",
    "Downtown Restaurant Group"
]

NAICS_CODES = {
    "541511": "Custom Computer Programming Services",
    "541512": "Computer Systems Design Services",
    "621111": "Offices of Physicians",
    "236220": "Commercial Building Construction",
    "722511": "Full-Service Restaurants",
    "484121": "General Freight Trucking"
}

STATES = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
COVERAGE_TYPES = ["General Liability", "Property", "Auto", "Workers Compensation"]


def generate_address(state=None):
    """Generate a realistic business address"""
    streets = ["Main St", "Oak Ave", "Park Blvd", "Commerce Dr", "Industrial Way"]
    cities = {
        "CA": ["Los Angeles", "San Francisco", "San Diego"],
        "NY": ["New York", "Buffalo", "Rochester"],
        "TX": ["Houston", "Dallas", "Austin"],
        "FL": ["Miami", "Tampa", "Orlando"]
    }
    
    state = state or random.choice(STATES)
    city = random.choice(cities.get(state, ["Springfield"]))
    street_num = random.randint(100, 9999)
    street = random.choice(streets)
    zip_code = f"{random.randint(10000, 99999)}"
    
    return {
        "street": f"{street_num} {street}",
        "city": city,
        "state": state,
        "zip": zip_code
    }


def prettify_xml(elem):
    """Return a pretty-printed XML string"""
    rough_string = tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def create_complete_submission(file_num):
    """Generate a complete, valid ACORD 103 submission"""
    root = Element('ACORD')
    root.set('xmlns', 'http://www.ACORD.org/standards/PC_Surety/ACORD1/xml/')
    
    # Add comment
    comment = Comment(f' COMPLETE SUBMISSION {file_num:03d} - All required fields present, all validations pass ')
    root.append(comment)
    
    # Submission metadata
    submission = SubElement(root, 'CommercialSubmission')
    SubElement(submission, 'SubmissionNumber').text = f"SUB-{uuid.uuid4().hex[:8].upper()}"
    SubElement(submission, 'SubmissionDate').text = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
    
    # Applicant information
    applicant = SubElement(submission, 'Applicant')
    
    # Business Info
    business_info = SubElement(applicant, 'BusinessInfo')
    SubElement(business_info, 'BusinessName').text = random.choice(BUSINESS_NAMES)
    naics = random.choice(list(NAICS_CODES.keys()))
    SubElement(business_info, 'NAICSCode').text = naics
    
    # Years in business (valid range)
    years = random.randint(3, 25)
    SubElement(business_info, 'YearsInBusiness').text = str(years)
    
    # Financial Info (consistent with employee count)
    financial_info = SubElement(applicant, 'FinancialInfo')
    employees = random.randint(10, 100)
    # Revenue consistent with employee count
    revenue = employees * random.randint(80000, 150000)
    SubElement(financial_info, 'AnnualRevenue').text = f"{revenue:.2f}"
    
    # Employee Info
    employee_info = SubElement(applicant, 'EmployeeInfo')
    SubElement(employee_info, 'TotalEmployees').text = str(employees)
    
    # Address
    addr = generate_address()
    address = SubElement(applicant, 'Address')
    SubElement(address, 'Street').text = addr['street']
    SubElement(address, 'City').text = addr['city']
    SubElement(address, 'State').text = addr['state']
    SubElement(address, 'PostalCode').text = addr['zip']
    
    # Coverage Request
    coverage_request = SubElement(submission, 'CoverageRequest')
    coverage_types = random.sample(COVERAGE_TYPES, k=random.randint(2, 3))
    SubElement(coverage_request, 'CoverageType').text = ", ".join(coverage_types)
    SubElement(coverage_request, 'Limits').text = "$1,000,000/$2,000,000"
    
    return root


def create_incomplete_submission(file_num, missing_fields):
    """Generate an incomplete submission with missing required fields"""
    root = Element('ACORD')
    root.set('xmlns', 'http://www.ACORD.org/standards/PC_Surety/ACORD1/xml/')
    
    # Add comment explaining what's missing
    missing_list = ", ".join(missing_fields)
    comment = Comment(f' INCOMPLETE SUBMISSION {file_num:03d} - Missing: {missing_list} ')
    root.append(comment)
    
    submission = SubElement(root, 'CommercialSubmission')
    SubElement(submission, 'SubmissionNumber').text = f"SUB-{uuid.uuid4().hex[:8].upper()}"
    SubElement(submission, 'SubmissionDate').text = datetime.now().isoformat()
    
    applicant = SubElement(submission, 'Applicant')
    
    # Business Info - conditionally add fields
    business_info = SubElement(applicant, 'BusinessInfo')
    if 'business_name' not in missing_fields:
        SubElement(business_info, 'BusinessName').text = random.choice(BUSINESS_NAMES)
    
    if 'naics_code' not in missing_fields:
        SubElement(business_info, 'NAICSCode').text = random.choice(list(NAICS_CODES.keys()))
    
    if 'years_in_business' not in missing_fields:
        SubElement(business_info, 'YearsInBusiness').text = str(random.randint(1, 20))
    
    # Financial Info
    if 'annual_revenue' not in missing_fields:
        financial_info = SubElement(applicant, 'FinancialInfo')
        SubElement(financial_info, 'AnnualRevenue').text = f"{random.randint(100000, 5000000):.2f}"
    
    # Employee Info
    if 'employee_count' not in missing_fields:
        employee_info = SubElement(applicant, 'EmployeeInfo')
        SubElement(employee_info, 'TotalEmployees').text = str(random.randint(5, 50))
    
    # Address
    if 'business_address' not in missing_fields:
        addr = generate_address()
        address = SubElement(applicant, 'Address')
        SubElement(address, 'Street').text = addr['street']
        SubElement(address, 'City').text = addr['city']
        SubElement(address, 'State').text = addr['state']
        SubElement(address, 'PostalCode').text = addr['zip']
    
    # Coverage Request
    if 'requested_coverage_types' not in missing_fields or 'requested_limits' not in missing_fields:
        coverage_request = SubElement(submission, 'CoverageRequest')
        if 'requested_coverage_types' not in missing_fields:
            SubElement(coverage_request, 'CoverageType').text = random.choice(COVERAGE_TYPES)
        if 'requested_limits' not in missing_fields:
            SubElement(coverage_request, 'Limits').text = "$500,000/$1,000,000"
    
    return root


def create_anomalous_submission(file_num, anomaly_type):
    """Generate a submission with data quality issues"""
    root = Element('ACORD')
    root.set('xmlns', 'http://www.ACORD.org/standards/PC_Surety/ACORD1/xml/')
    
    comment = Comment(f' ANOMALOUS SUBMISSION {file_num:03d} - Issue: {anomaly_type} ')
    root.append(comment)
    
    submission = SubElement(root, 'CommercialSubmission')
    SubElement(submission, 'SubmissionNumber').text = f"SUB-{uuid.uuid4().hex[:8].upper()}"
    SubElement(submission, 'SubmissionDate').text = datetime.now().isoformat()
    
    applicant = SubElement(submission, 'Applicant')
    
    # Business Info
    business_info = SubElement(applicant, 'BusinessInfo')
    SubElement(business_info, 'BusinessName').text = random.choice(BUSINESS_NAMES)
    
    if anomaly_type == "invalid_naics_code":
        # Invalid NAICS code (wrong format)
        SubElement(business_info, 'NAICSCode').text = "12345"  # Only 5 digits instead of 6
    else:
        SubElement(business_info, 'NAICSCode').text = random.choice(list(NAICS_CODES.keys()))
    
    if anomaly_type == "revenue_employee_mismatch":
        # Small employee count but huge revenue (inconsistent)
        SubElement(business_info, 'YearsInBusiness').text = "5"
        financial_info = SubElement(applicant, 'FinancialInfo')
        SubElement(financial_info, 'AnnualRevenue').text = "50000000.00"  # $50M
        employee_info = SubElement(applicant, 'EmployeeInfo')
        SubElement(employee_info, 'TotalEmployees').text = "3"  # Only 3 employees
    elif anomaly_type == "new_business_high_revenue":
        # New business with suspiciously high revenue
        SubElement(business_info, 'YearsInBusiness').text = "1"  # Only 1 year old
        financial_info = SubElement(applicant, 'FinancialInfo')
        SubElement(financial_info, 'AnnualRevenue').text = "25000000.00"  # $25M
        employee_info = SubElement(applicant, 'EmployeeInfo')
        SubElement(employee_info, 'TotalEmployees').text = "50"
    else:
        SubElement(business_info, 'YearsInBusiness').text = str(random.randint(2, 15))
        financial_info = SubElement(applicant, 'FinancialInfo')
        SubElement(financial_info, 'AnnualRevenue').text = f"{random.randint(500000, 5000000):.2f}"
        employee_info = SubElement(applicant, 'EmployeeInfo')
        SubElement(employee_info, 'TotalEmployees').text = str(random.randint(10, 75))
    
    # Address
    addr = generate_address()
    address = SubElement(applicant, 'Address')
    SubElement(address, 'Street').text = addr['street']
    SubElement(address, 'City').text = addr['city']
    SubElement(address, 'State').text = addr['state']
    SubElement(address, 'PostalCode').text = addr['zip']
    
    # Coverage Request
    coverage_request = SubElement(submission, 'CoverageRequest')
    SubElement(coverage_request, 'CoverageType').text = ", ".join(random.sample(COVERAGE_TYPES, k=2))
    SubElement(coverage_request, 'Limits').text = "$1,000,000/$2,000,000"
    
    return root


def main():
    """Generate all sample ACORD XML files"""
    output_dir = Path(__file__).parent.parent / 'data' / 'sample_acord'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎯 Generating ACORD 103 Sample XML Files...")
    print(f"📁 Output directory: {output_dir}")
    print()
    
    # Generate 2 complete submissions
    for i in range(1, 3):
        filename = f"complete_submission_{i:03d}.xml"
        xml_tree = create_complete_submission(i)
        xml_string = prettify_xml(xml_tree)
        
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        print(f"✅ Generated: {filename} (COMPLETE - all validations pass)")
    
    # Generate 2 incomplete submissions with different missing fields
    incomplete_configs = [
        (['business_name', 'naics_code'], 1),
        (['annual_revenue', 'employee_count', 'requested_limits'], 2)
    ]
    
    for missing_fields, i in incomplete_configs:
        filename = f"incomplete_submission_{i:03d}.xml"
        xml_tree = create_incomplete_submission(i, missing_fields)
        xml_string = prettify_xml(xml_tree)
        
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        print(f"⚠️  Generated: {filename} (INCOMPLETE - missing {', '.join(missing_fields)})")
    
    # Generate 2 anomalous submissions
    anomaly_configs = [
        ("revenue_employee_mismatch", 1),
        ("new_business_high_revenue", 2)
    ]
    
    for anomaly_type, i in anomaly_configs:
        filename = f"anomalous_submission_{i:03d}.xml"
        xml_tree = create_anomalous_submission(i, anomaly_type)
        xml_string = prettify_xml(xml_tree)
        
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        print(f"🔴 Generated: {filename} (ANOMALOUS - {anomaly_type})")
    
    print()
    print(f"✨ Successfully generated 6 ACORD XML files in {output_dir}")
    print()
    print("📊 Summary:")
    print("  - 2 Complete submissions (all validations pass)")
    print("  - 2 Incomplete submissions (missing required fields)")
    print("  - 2 Anomalous submissions (data quality issues)")


if __name__ == '__main__':
    main()
