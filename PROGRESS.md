# CKAN 2.11 Migration Progress - ckanext-harvest

Migration of ckanext-harvest from CKAN 2.9/2.10 to CKAN 2.11 with Python 3.10.

## Change Log

### 1. Update CI/CD to CKAN 2.11 Only

**Date**: 2026-01-07

**Problem**:
The GitHub Actions workflow was testing against multiple CKAN versions (2.9, 2.10, 2.11), which is unnecessary for a CKAN 2.11-only migration.

**Solution**:
Updated `.github/workflows/test.yml` to only test CKAN 2.11 with Python 3.10:
- Removed Python 3.9 from lint job matrix
- Removed CKAN 2.9 and 2.10 from test job matrix
- Hardcoded service images to CKAN 2.11 versions (solr9, postgres 2.11)

**Files Modified**:
- `.github/workflows/test.yml`

**Status**: ⏳ Waiting for test verification

---

### 2. Fix SQLAlchemy Table Existence Checks for CKAN 2.11

**Date**: 2026-01-07

**Problem**:
Tests failed during the "Setup extension" step with error:
```
sqlalchemy.exc.UnboundExecutionError: Table object 'package' is not bound to an Engine or Connection.
```

The issue occurred in `ckanext/harvest/model/__init__.py:50` when calling `model.package_table.exists()` during plugin configuration. In CKAN 2.11, the database engine isn't bound yet during the plugin's `configure()` phase, so direct `.exists()` calls fail.

**Root Cause**:
- CKAN 2.11 changed the initialization sequence
- The `.exists()` method on SQLAlchemy tables requires a bound engine
- During plugin configuration, the engine is not yet available
- The old approach worked in CKAN 2.9/2.10 but breaks in 2.11

**Solution**:
Replaced `.exists()` calls with SQLAlchemy Inspector pattern:
- Added try-except block around Inspector creation to handle cases where engine isn't ready
- Use `inspector.get_table_names()` to get list of existing tables
- Check for table existence by name in the list instead of calling `.exists()`
- Removed duplicate Inspector creation later in the function
- This pattern is already used elsewhere in the same file (line 71+)

**Files Modified**:
- `ckanext/harvest/model/__init__.py` (lines 44-83)

**Changes**:
- Line 50-57: Wrap Inspector creation in try-except, get table names list
- Line 59-61: Check 'package' in table list instead of `.exists()`
- Line 63: Check 'harvest_source' in table list instead of `.exists()`
- Line 76-81: Removed duplicate engine import and Inspector creation
- Line 67-73, 82, 88, 92, 96, 100, 105: Added `bind=engine` parameter to all `.create()` calls for tables and indexes

**Status**: ✅ FIXED - Setup now completes successfully

**Result**: Database initialization and table creation now works correctly. Tests begin execution but fail during test collection due to unrelated import issue (see next entry).

**Note**: After first test run, discovered that `.create()` methods also need the engine bound. Updated all table and index creation calls to include `bind=engine` parameter.

---

### 3. Fix nose imports for pytest compatibility

**Date**: 2026-01-07

**Problem**:
Test collection failed with:
```
ModuleNotFoundError: No module named 'nose'
```

The test file `ckanext/harvest/tests/test_timeouts.py` imports from `nose.tools` which is not available in CKAN 2.11.

**Root Cause**:
- CKAN 2.11 uses pytest instead of the nose testing framework
- Old test files still have `from nose.tools import assert_equal, assert_in` imports
- These need to be replaced with standard Python assertions

**Solution**:
- Removed `from nose.tools import assert_equal, assert_in` import
- Replaced all `assert_equal(a, b)` with `assert a == b` (14 occurrences)
- Replaced all `assert_in(a, b)` with `assert a in b` (2 occurrences)

**Files Modified**:
- `ckanext/harvest/tests/test_timeouts.py`

**Status**: ✅ FIXED - Tests now collect and run successfully

**Result**: Test collection now works. Tests run with 16 failures (to be addressed separately).

---

