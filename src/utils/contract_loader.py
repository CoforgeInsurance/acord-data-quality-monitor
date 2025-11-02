"""
Contract Loader Utility

Loads and validates YAML contracts for code generation and runtime validation.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ContractLoader:
    """Load and access YAML data contracts"""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """
        Initialize contract loader.
        
        Args:
            contracts_dir: Path to contracts directory. Defaults to ../contracts relative to this file.
        """
        if contracts_dir is None:
            # Default to contracts directory in project root
            contracts_dir = Path(__file__).parent.parent.parent / 'contracts'
        
        self.contracts_dir = Path(contracts_dir)
        if not self.contracts_dir.exists():
            raise FileNotFoundError(f"Contracts directory not found: {self.contracts_dir}")
        
        self._cache = {}
    
    def load_contract(self, contract_name: str) -> Dict[str, Any]:
        """
        Load a YAML contract by name.
        
        Args:
            contract_name: Name of contract file (with or without .yml extension)
        
        Returns:
            Dictionary containing contract data
        
        Raises:
            FileNotFoundError: If contract file doesn't exist
            yaml.YAMLError: If contract is not valid YAML
        """
        # Add .yml extension if not present
        if not contract_name.endswith('.yml') and not contract_name.endswith('.yaml'):
            contract_name = f"{contract_name}.yml"
        
        # Check cache
        if contract_name in self._cache:
            return self._cache[contract_name]
        
        # Load from file
        contract_path = self.contracts_dir / contract_name
        if not contract_path.exists():
            raise FileNotFoundError(f"Contract not found: {contract_path}")
        
        with open(contract_path, 'r', encoding='utf-8') as f:
            contract_data = yaml.safe_load(f)
        
        # Cache and return
        self._cache[contract_name] = contract_data
        return contract_data
    
    def get_quality_rules_contract(self) -> Dict[str, Any]:
        """Load submission_quality_rules.yml contract"""
        return self.load_contract('submission_quality_rules.yml')
    
    def get_dim_submission_contract(self) -> Dict[str, Any]:
        """Load dim_submission.yml contract"""
        return self.load_contract('dim_submission.yml')
    
    def get_fact_quality_check_contract(self) -> Dict[str, Any]:
        """Load fact_quality_check.yml contract"""
        return self.load_contract('fact_quality_check.yml')
    
    def get_field_mapping(self, contract_name: str, field_name: str) -> Optional[Dict[str, Any]]:
        """
        Get field mapping from a contract.
        
        Args:
            contract_name: Name of contract
            field_name: Name of field to lookup
        
        Returns:
            Field definition dict or None if not found
        """
        contract = self.load_contract(contract_name)
        
        # Search in schema section
        if 'schema' in contract:
            for field in contract['schema']:
                if field.get('name') == field_name:
                    return field
        
        # Search in required_fields section
        if 'required_fields' in contract:
            for category, fields in contract['required_fields'].items():
                for field in fields:
                    if field.get('field') == field_name:
                        return field
        
        return None
    
    def list_contracts(self) -> list:
        """List all available contract files"""
        return [f.name for f in self.contracts_dir.glob('*.yml')]
