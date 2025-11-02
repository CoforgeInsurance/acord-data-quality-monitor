"""Setup configuration for ACORD Data Quality Monitor"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="acord-data-quality-monitor",
    version="1.0.0",
    author="Coforge Insurance Data Engineering Team",
    description="AI-Agentic Data Quality Monitor for ACORD Insurance Submissions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CoforgeInsurance/acord-data-quality-monitor",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "pyyaml>=6.0.1",
        "pydantic>=2.5.0",
        "xmltodict>=0.13.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
        ],
        "dbt": [
            "dbt-core>=1.7.0",
            "dbt-duckdb>=1.7.0",
        ],
        "quality": [
            "great-expectations>=0.18.0",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Office/Business :: Financial :: Insurance",
    ],
    keywords="insurance acord data-quality ai-agentic contract-driven",
)
