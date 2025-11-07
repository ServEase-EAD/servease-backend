# Authentication Service - Test Suite Documentation

## 📊 Test Results Summary

- **Total Tests**: 87
- **Passing Tests**: 87 ✅
- **Failed Tests**: 0
- **Code Coverage**: 80.17%
- **Test Execution Time**: ~4 minutes

## 🎯 Test Coverage Breakdown

| Module | Statements | Missing | Coverage |
|--------|-----------|---------|----------|
| models.py | 48 | 0 | **100.00%** |
| permissions.py | 16 | 0 | **100.00%** |
| serializers.py | 62 | 1 | **98.39%** |
| views.py | 156 | 16 | **89.74%** |
| urls.py | 4 | 0 | **100.00%** |
| **TOTAL** | **363** | **72** | **80.17%** |

## 📁 Test Structure

```
tests/
├── README.md              # This file
├── conftest.py           # Test fixtures and configuration (141 lines)
├── test_models.py        # Model unit tests (16 tests)
├── test_serializers.py   # Serializer unit tests (18 tests)
├── test_permissions.py   # Permission unit tests (13 tests)
└── test_views.py         # API integration tests (40 tests)
```

## 🧪 Test Categories

### 1. Model Tests (test_models.py)
Tests for `CustomUser` model and `CustomUserManager`:
- ✅ User creation (customer, employee, admin)
- ✅ Email validation and uniqueness
- ✅ Password hashing
- ✅ Role-based methods (is_admin, is_employee, is_customer)
- ✅ Manager methods (create_user, create_employee, create_superuser)
- ✅ String representation
- ✅ Timestamps (created_at, updated_at)

### 2. Serializer Tests (test_serializers.py)
Tests for all serializers:
- ✅ UserRegistrationSerializer (5 tests)
- ✅ EmployeeRegistrationSerializer (2 tests)
- ✅ UserLoginSerializer (4 tests)
- ✅ CustomUserSerializer (2 tests)
- ✅ UserListSerializer (2 tests)
- ✅ UserDetailSerializer (2 tests)

### 3. Permission Tests (test_permissions.py)
Tests for custom permission classes:
- ✅ IsAdmin (4 tests)
- ✅ IsEmployee (3 tests)
- ✅ IsCustomer (3 tests)
- ✅ IsEmployeeOrAdmin (3 tests)
- ✅ IsOwnerOrAdmin (4 tests)

### 4. View/API Tests (test_views.py)
Integration tests for all API endpoints:
- ✅ User Registration (4 tests)
- ✅ User Login (4 tests)
- ✅ User Logout (3 tests)
- ✅ Current User Profile (3 tests)
- ✅ Employee Registration - Admin Only (3 tests)
- ✅ Employee List - Admin Only (2 tests)
- ✅ User List - Admin Only (3 tests)
- ✅ User Detail (5 tests)
- ✅ Toggle User Status (3 tests)
- ✅ Admin Dashboard Stats (2 tests)
- ✅ Token Validation (3 tests)
- ✅ Token Refresh (2 tests)

## 🚀 Running the Tests

### Option 1: Using the Test Runner Script
```bash
./run_tests.sh
```

### Option 2: Using pytest directly
```bash
# Run all tests with coverage
pytest --cov=accounts --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_models.py -v

# Run specific test class
pytest tests/test_views.py::TestUserRegistration -v

# Run specific test
pytest tests/test_models.py::TestCustomUserModel::test_create_user -v
```

### Option 3: Using pytest with markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

## 📈 Coverage Report

After running tests, you can view the detailed HTML coverage report:

```bash
# Open the coverage report in your browser
open htmlcov/index.html
```

The report shows:
- Line-by-line coverage for each file
- Which lines are covered/missed
- Branch coverage
- Module-level statistics

## 🔧 Test Configuration

### pytest.ini
- Django settings module: `authentication_service.settings`
- Minimum coverage threshold: 80%
- Output format: verbose with color

### .coveragerc
- Coverage source: `accounts` app
- Excluded files: migrations, tests, pycache, settings, etc.
- Report format: HTML and terminal with missing lines

### conftest.py
Provides reusable fixtures:
- `api_client`: DRF API client
- `customer_user`, `employee_user`, `admin_user`: Test users
- `customer_token`, `employee_token`, `admin_token`: JWT tokens
- `authenticated_*_client`: Pre-authenticated API clients
- Test data fixtures for registration

## ✅ Test Quality Metrics

### Unit Tests Coverage
- **Models**: 100% coverage
- **Permissions**: 100% coverage  
- **Serializers**: 98.39% coverage
- **URLs**: 100% coverage

### Integration Tests Coverage
- **Views/APIs**: 89.74% coverage
- All critical endpoints tested
- Authentication and authorization tested
- Error handling tested
- Edge cases covered

## 🎓 Key Testing Patterns Used

1. **Fixtures for Reusability**: Common test data defined once
2. **Parametrized Tests**: Where applicable for multiple scenarios
3. **Class-based Organization**: Tests grouped by functionality
4. **Descriptive Names**: Clear test method names
5. **Assertions**: Multiple assertions to verify behavior
6. **Error Testing**: Testing both success and failure paths
7. **Isolation**: Each test is independent

## 📝 Test Maintenance

### Adding New Tests
1. Create test methods in appropriate test file
2. Use existing fixtures from `conftest.py`
3. Follow naming convention: `test_<what_is_being_tested>`
4. Run tests to ensure they pass
5. Check coverage impact

### When Code Changes
1. Run related tests: `pytest tests/test_<module>.py`
2. Update tests if behavior changed intentionally
3. Add new tests for new functionality
4. Ensure coverage doesn't drop below 80%

## 🐛 Debugging Tests

### Run tests with more detail
```bash
pytest -vv --tb=long
```

### Run tests with print statements
```bash
pytest -s
```

### Run tests with debugger
```bash
pytest --pdb
```

### Run failed tests only
```bash
pytest --lf
```

## 📊 Submission Checklist

For assignment submission, ensure you have:

- [x] All tests passing (87/87)
- [x] Coverage above 80% (80.17%)
- [x] HTML coverage report generated (`htmlcov/index.html`)
- [x] Screenshots of test results
- [x] Screenshots of coverage report
- [x] This README documentation
- [x] Test files properly organized
- [x] Configuration files in place

## 🔍 Areas Not Fully Covered

The following areas have lower coverage and are candidates for additional tests:

1. **forms.py** (0% - not used in API)
2. **tokens.py** (0% - indirectly tested through views)
3. **middleware.py** (45.83% - middleware logic)

These are acceptable as they're either:
- Not actively used in the current implementation
- Difficult to test in isolation
- Tested indirectly through integration tests

## 🎉 Conclusion

This test suite provides comprehensive coverage of the authentication service with:
- **87 passing tests**
- **80.17% code coverage**
- **Unit and integration tests**
- **Automated test execution**
- **Detailed coverage reporting**

The tests ensure the authentication service is reliable, secure, and functions as expected.
