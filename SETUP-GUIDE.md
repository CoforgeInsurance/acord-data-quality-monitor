# Local Setup Guide

## Steps to Fix the CI/CD Pipeline

### 1. Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Install dbt
```powershell
pip install dbt-core dbt-duckdb
```

### 3. Create the target directory for DuckDB
```powershell
mkdir dbt_project\target -Force
```

### 4. Initialize the dbt project
```powershell
cd dbt_project
dbt debug --profiles-dir .
```

### 5. Run dbt models to create the database
```powershell
dbt run --profiles-dir .
```

### 6. Run dbt tests
```powershell
dbt test --profiles-dir .
```

### 7. Run Python tests
```powershell
cd ..
pytest tests/ -v
```

### 8. Commit and push the fixed workflow
```powershell
git add .github/workflows/ci.yml
git commit -m "fix: Add database initialization step to dbt workflow"
git push origin main
```

## What Was Fixed

1. **Added target directory creation** - The workflow now creates dbt_project/target before running dbt
2. **Added dbt run step** - This initializes the DuckDB database and creates tables before running tests
3. **Removed continue-on-error** - Tests now properly fail if there are issues

## Expected Results

After pushing this fix:
- ✅ Validate YAML Contracts - Should pass
- ✅ Test Python Code - Should pass
- ✅ Test dbt Models - Should now pass (previously failing)
- ✅ Code Quality Checks - Should pass

