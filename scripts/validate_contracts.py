"""
Validate YAML Contracts

Ensures all YAML contracts are:
1. Valid YAML syntax
2. Have required fields
3. Follow contract schema conventions
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List


class ContractValidator:
    """Validate YAML data contracts"""
    
    def __init__(self, contracts_dir: Path):
        self.contracts_dir = contracts_dir
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> bool:
        """
        Validate all contracts in the directory.
        
        Returns:
            True if all validations pass, False otherwise
        """
        print("🔍 Validating YAML Contracts...")
        print(f"📁 Contracts directory: {self.contracts_dir}")
        print()
        
        contract_files = list(self.contracts_dir.glob('*.yml'))
        
        if not contract_files:
            self.errors.append("No YAML contract files found")
            return False
        
        all_valid = True
        
        for contract_file in contract_files:
            if contract_file.name == 'README.md':
                continue
            
            print(f"📄 Validating: {contract_file.name}")
            
            if not self.validate_contract_file(contract_file):
                all_valid = False
        
        print()
        self.print_summary()
        
        return all_valid
    
    def validate_contract_file(self, contract_path: Path) -> bool:
        """Validate a single contract file"""
        try:
            # Load YAML
            with open(contract_path, 'r', encoding='utf-8') as f:
                contract = yaml.safe_load(f)
            
            if contract is None:
                self.errors.append(f"{contract_path.name}: Empty contract file")
                return False
            
            # Validate required top-level fields
            required_fields = ['contract_version', 'contract_type', 'description', 'owner']
            for field in required_fields:
                if field not in contract:
                    self.errors.append(f"{contract_path.name}: Missing required field '{field}'")
                    return False
            
            # Validate based on contract type
            contract_type = contract['contract_type']
            
            if contract_type == 'quality_rules':
                return self.validate_quality_rules_contract(contract_path.name, contract)
            elif contract_type == 'data_warehouse_dimension':
                return self.validate_dimension_contract(contract_path.name, contract)
            elif contract_type == 'data_warehouse_fact':
                return self.validate_fact_contract(contract_path.name, contract)
            else:
                self.warnings.append(f"{contract_path.name}: Unknown contract_type '{contract_type}'")
                return True
            
        except yaml.YAMLError as e:
            self.errors.append(f"{contract_path.name}: Invalid YAML - {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"{contract_path.name}: Validation error - {str(e)}")
            return False
    
    def validate_quality_rules_contract(self, filename: str, contract: Dict[str, Any]) -> bool:
        """Validate quality_rules contract"""
        valid = True
        
        # Should have required_fields
        if 'required_fields' not in contract:
            self.errors.append(f"{filename}: quality_rules contract missing 'required_fields'")
            valid = False
        else:
            # Validate required_fields structure
            for category, fields in contract['required_fields'].items():
                if not isinstance(fields, list):
                    self.errors.append(f"{filename}: required_fields.{category} should be a list")
                    valid = False
                else:
                    for field_def in fields:
                        if 'field' not in field_def:
                            self.errors.append(f"{filename}: Field definition missing 'field' name in {category}")
                            valid = False
                        if 'acord_path' not in field_def:
                            self.errors.append(f"{filename}: Field '{field_def.get('field', 'unknown')}' missing 'acord_path'")
                            valid = False
        
        # Should have consistency_checks
        if 'consistency_checks' not in contract:
            self.warnings.append(f"{filename}: No consistency_checks defined")
        else:
            for check in contract['consistency_checks']:
                required = ['rule_id', 'name', 'description', 'severity', 'logic']
                for field in required:
                    if field not in check:
                        self.errors.append(f"{filename}: Consistency check missing '{field}'")
                        valid = False
        
        # Should have quality_thresholds
        if 'quality_thresholds' not in contract:
            self.warnings.append(f"{filename}: No quality_thresholds defined")
        else:
            for threshold in contract['quality_thresholds']:
                required = ['metric', 'description', 'target', 'minimum', 'calculation']
                for field in required:
                    if field not in threshold:
                        self.errors.append(f"{filename}: Quality threshold missing '{field}'")
                        valid = False
        
        print(f"  ✅ Quality rules contract validated")
        return valid
    
    def validate_dimension_contract(self, filename: str, contract: Dict[str, Any]) -> bool:
        """Validate data_warehouse_dimension contract"""
        valid = True
        
        # Should have table name
        if 'table' not in contract:
            self.errors.append(f"{filename}: Missing 'table' name")
            valid = False
        
        # Should have schema
        if 'schema' not in contract:
            self.errors.append(f"{filename}: Missing 'schema' definition")
            valid = False
        else:
            # Validate schema fields
            for field_def in contract['schema']:
                required = ['name', 'type', 'nullable', 'description']
                for field in required:
                    if field not in field_def:
                        self.errors.append(f"{filename}: Schema field missing '{field}'")
                        valid = False
                
                # Validate at least one field is primary key
            has_primary_key = any(f.get('primary_key', False) for f in contract['schema'])
            if not has_primary_key:
                self.warnings.append(f"{filename}: No primary_key defined in schema")
        
        # Should have quality_rules
        if 'quality_rules' not in contract:
            self.warnings.append(f"{filename}: No quality_rules defined")
        
        # Should have sla
        if 'sla' not in contract:
            self.warnings.append(f"{filename}: No SLA defined")
        
        print(f"  ✅ Dimension contract validated")
        return valid
    
    def validate_fact_contract(self, filename: str, contract: Dict[str, Any]) -> bool:
        """Validate data_warehouse_fact contract"""
        valid = True
        
        # Should have table name
        if 'table' not in contract:
            self.errors.append(f"{filename}: Missing 'table' name")
            valid = False
        
        # Should have schema
        if 'schema' not in contract:
            self.errors.append(f"{filename}: Missing 'schema' definition")
            valid = False
        else:
            # Validate schema fields
            for field_def in contract['schema']:
                required = ['name', 'type', 'nullable', 'description']
                for field in required:
                    if field not in field_def:
                        self.errors.append(f"{filename}: Schema field missing '{field}'")
                        valid = False
        
        print(f"  ✅ Fact contract validated")
        return valid
    
    def print_summary(self):
        """Print validation summary"""
        print("=" * 60)
        print("📊 Validation Summary")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All contracts are valid!")
        elif not self.errors:
            print(f"\n✅ All contracts are valid (with {len(self.warnings)} warnings)")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} errors")


def main():
    """Main entry point"""
    # Get contracts directory
    script_dir = Path(__file__).parent
    contracts_dir = script_dir.parent / 'contracts'
    
    if not contracts_dir.exists():
        print(f"❌ Contracts directory not found: {contracts_dir}")
        sys.exit(1)
    
    # Validate
    validator = ContractValidator(contracts_dir)
    success = validator.validate_all()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
