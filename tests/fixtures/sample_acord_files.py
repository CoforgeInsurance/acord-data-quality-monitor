"""
Test fixtures for ACORD XML sample files and test data
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_acord_dir():
    """Return path to sample ACORD XML directory"""
    return Path(__file__).parent.parent.parent / 'data' / 'sample_acord'


@pytest.fixture
def complete_submission_files(sample_acord_dir):
    """Return paths to complete ACORD submission files"""
    return [
        sample_acord_dir / 'complete_submission_001.xml',
        sample_acord_dir / 'complete_submission_002.xml'
    ]


@pytest.fixture
def incomplete_submission_files(sample_acord_dir):
    """Return paths to incomplete ACORD submission files"""
    return [
        sample_acord_dir / 'incomplete_submission_001.xml',
        sample_acord_dir / 'incomplete_submission_002.xml'
    ]


@pytest.fixture
def anomalous_submission_files(sample_acord_dir):
    """Return paths to anomalous ACORD submission files"""
    return [
        sample_acord_dir / 'anomalous_submission_001.xml',
        sample_acord_dir / 'anomalous_submission_002.xml'
    ]


@pytest.fixture
def all_sample_files(complete_submission_files, incomplete_submission_files, anomalous_submission_files):
    """Return all sample ACORD XML files"""
    return complete_submission_files + incomplete_submission_files + anomalous_submission_files


@pytest.fixture
def contracts_dir():
    """Return path to contracts directory"""
    return Path(__file__).parent.parent.parent / 'contracts'
