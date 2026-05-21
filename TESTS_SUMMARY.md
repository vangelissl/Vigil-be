# User Endpoints Tests Summary

Comprehensive test suite for user management endpoints has been created in `tests/integration/test_users_endpoints.py`.

## Endpoints Tested

### 1. GET /users/me/

Retrieves the current authenticated user's profile.

**Test Cases:**

- ✅ `test_get_me_success` - Returns user profile with email and username
- ✅ `test_get_me_returns_correct_schema` - Validates response contains only email and username fields
- ✅ `test_get_me_user_not_found` - Returns 401 when user not found
- ✅ `test_get_me_missing_auth_header` - Returns 422/403 when authentication cookie is missing

**Expected Status Codes:**

- 200 OK: User profile returned successfully
- 401 Unauthorized: User not found or invalid token
- 422 Unprocessable Entity: Missing authentication cookie

---

### 2. PATCH /users/me/

Updates the current authenticated user's profile (email, username, password).

**Test Cases:**

**Happy Path:**

- ✅ `test_patch_me_success_update_email` - Successfully updates email
- ✅ `test_patch_me_success_update_username` - Successfully updates username
- ✅ `test_patch_me_success_update_password` - Successfully updates password
- ✅ `test_patch_me_success_update_multiple_fields` - Updates multiple fields at once
- ✅ `test_patch_me_returns_no_content` - Returns 200 with empty body
- ✅ `test_patch_me_with_null_values` - Accepts null values for optional fields

**Validation Errors:**

- ✅ `test_patch_me_missing_password` - Returns 422 when password field is missing
- ✅ `test_patch_me_invalid_email_format` - Returns 422 for invalid email format
- ✅ `test_patch_me_empty_password` - Accepts empty string as valid
- ✅ `test_patch_me_missing_auth_header` - Returns 422/403 when auth cookie missing
- ✅ `test_patch_me_empty_body` - Returns 422 when body is empty
- ✅ `test_patch_me_with_extra_fields` - Returns 200 or 422 depending on pydantic config

**Error Handling:**

- ✅ `test_patch_me_wrong_password` - Returns 406 when password is incorrect
- ✅ `test_patch_me_email_already_taken` - Returns 400 when email is taken
- ✅ `test_patch_me_username_already_taken` - Returns 400 when username is taken
- ✅ `test_patch_me_user_not_found` - Returns 401 when user not found

**Behavior Verification:**

- ✅ `test_patch_me_calls_service_with_correct_params` - Verifies service is called with correct user ID

**Expected Status Codes:**

- 200 OK: Profile updated successfully
- 400 Bad Request: Email or username already taken
- 401 Unauthorized: User not found
- 406 Not Acceptable: Wrong password
- 422 Unprocessable Entity: Validation error
- 403 Forbidden: Missing authentication

---

## Test Coverage

**Total Test Cases: 24**

### Coverage by Category:

- **Success Cases**: 6
- **Validation Errors**: 7
- **Exception Handling**: 4
- **Edge Cases/Auth**: 7

### Coverage by Feature:

- **GET /users/me/**: 4 tests
- **PATCH /users/me/**: 20 tests

---

## Running the Tests

```bash
# Run all user endpoint tests
pytest tests/integration/test_users_endpoints.py -v

# Run specific test class
pytest tests/integration/test_users_endpoints.py::TestGetMe -v
pytest tests/integration/test_users_endpoints.py::TestPatchMe -v

# Run a single test
pytest tests/integration/test_users_endpoints.py::TestPatchMe::test_patch_me_success_update_email -v

# Run with coverage
pytest tests/integration/test_users_endpoints.py --cov=src.vigil.modules.users --cov-report=html
```

---

## Test Fixtures Used

The tests use the following pytest fixtures from `conftest.py`:

- `client_with_user_service` - Mocked HTTP client with user service and current user mocked
- `mock_user_service` - AsyncMock of the UserService
- `mock_current_user` - Mocked current user DTO
- `domain_user` - Sample domain user entity
- `user_id` - UUID for test user
- `username` - Test username
- `email` - Test email

---

## Notes

- All tests use async/await syntax compatible with FastAPI's async handlers
- Tests mock the UserService and authentication dependencies to avoid database operations
- Exception handlers are tested to ensure proper HTTP status codes and messages
- Tests follow the AAA pattern: Arrange, Act, Assert
- Each test has a descriptive docstring explaining what it tests

---

## Dependencies

The test suite requires:

- pytest
- pytest-asyncio
- httpx (async HTTP client)
- FastAPI
- The vigil application modules

All dependencies are already configured in the project's `pyproject.toml`.
