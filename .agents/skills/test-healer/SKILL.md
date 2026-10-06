---
name: test-healer
description: >
  Use when: (1) "verify the tests", (2) "run the tests and fix them", (3) "test heal",
  (4) after test-generator creates tests, (5) tests are failing and need fixing.
---

# Test Healer

Review, execute, and repair test code to ensure quality and all tests pass.

## Persona

As a test quality assurance expert:
- Thoroughly review the quality of the written test code
- Analyze test results to identify the causes of failures
- Fix **test code issues** directly and report **implementation code issues**
- Repeat until all tests pass

## Scope

This skill targets the test files for a **specific feature**.

### Input
- Feature name (e.g., `research_favorite`)
- Or a test file path (e.g., `tests/services/test_research_favorite_service.py`)

### Target Files
```
tests/controllers/test_{feature}_controller.py
tests/services/test_{feature}_service.py
tests/repositories/test_{feature}_repository.py
```

### Reference
- `tests/conftest.py` - Global fixture definitions
- `tests/utils/helpers.py` - assert_success_response, assert_error_response
- `tests/factories/` - Factory classes
- `tests/CLAUDE.md` - Project testing conventions
- **Existing passing tests in the same layer** - Reference patterns

## Prerequisites

**Must verify before running tests:**
```bash
export ENV=test  # Required! Without it, bootstrap.py calls sys.exit(1)
```

## Workflow

```
┌─────────────────┐
│  1. Review      │ Review test code quality
└────────┬────────┘
         ▼
┌─────────────────┐
│  2. Execute     │ Run ENV=test pytest
└────────┬────────┘
         ▼
    ┌────┴────┐
    │ Pass?   │
    └────┬────┘
    Yes  │  No
    ▼    ▼
┌──────┐ ┌─────────────────┐
│ Done │ │ 3. Analyze      │ Analyze failure causes
└──────┘ └────────┬────────┘
                  ▼
         ┌───────────────────┐
         │ Test code issue?  │
         └────────┬──────────┘
         Yes      │      No
         ▼        ▼
┌─────────────┐  ┌─────────────────┐
│ 4. Repair   │  │ Report impl bug │
└──────┬──────┘  └─────────────────┘
       │
       └──────► (Rerun pytest, up to 3 times)
```

## Phase 1: Review

Test code quality review checklist:

### Convention Compliance
- [ ] Use the AAA pattern (Arrange-Act-Assert)
- [ ] State the test purpose in a Korean-language docstring
- [ ] Use the correct fixture (one appropriate for the layer)
- [ ] Follow the naming convention (`test_{method}_{case}`)

### Coverage
- [ ] Include success cases
- [ ] Include error/exception cases
- [ ] Consider edge cases (empty data, boundary values, etc.)
- [ ] PATCH: Include partial-update scenarios

### Mock Configuration
- [ ] Is the correct target being mocked?
- [ ] Are `return_value` / `side_effect` configured appropriately?
- [ ] Is `assert_called_once_with` used correctly?
- [ ] **Is the Factory method appropriate for the layer** (`build` vs. `build_response`)?

### Layer-Specific Pattern References
Before making changes, read **existing passing tests in the same layer** to understand project patterns:
```bash
# Refer to other test files in the same layer
tests/controllers/test_research_favorite_controller.py
tests/services/test_research_favorite_service.py
```

## Phase 2: Execute

```bash
# Always include ENV=test
ENV=test pytest tests/{layer}/test_{feature}_{layer}.py -v

# Rerun only failed tests
ENV=test pytest tests/{layer}/test_{feature}_{layer}.py -v --ff

# Stop at the first failure
ENV=test pytest tests/{layer}/test_{feature}_{layer}.py -v -x
```

## Phase 3: Analyze

Classify the causes of failures:

### Test Code Issues (To Fix)
- Mock configuration errors (incorrect `return_value` or `side_effect`)
- Assertion errors (expected value mismatch)
- Fixture usage errors
- Import errors
- Asynchronous handling errors (e.g., missing `@pytest.mark.asyncio`)

### Implementation Code Issues (To Report)
- Actual business logic bugs
- API response format changes
- Exception type mismatches
- Dependency injection errors

## Phase 4: Repair

### Common Fixes

**1. Confusing Factory methods (Model vs. Schema)**
```python
# WRONG: Return a Model in a Controller test
mock_service.get.return_value = ResearchDesignFactory.build()  # SQLAlchemy Model

# CORRECT: Controller tests require a Response schema
mock_service.get.return_value = ResearchDesignFactory.build_response()  # Pydantic Schema
```

**2. Missing fixture to retrieve a service from mock_services**
```python
# WRONG: Using an undefined fixture causes a "fixture not found" error
def test_get(self, mock_research_design_service):  # This fixture is not defined!

# CORRECT: Define a fixture that retrieves the service from mock_services
@pytest.fixture
def mock_research_design_service(self, mock_services):
    return mock_services["research_design_service"]
```

**3. Using MagicMock with model_validate**
```python
# WRONG: MagicMock fails when the Service uses model_validate
mock_repo.get.return_value = MagicMock(spec=ResearchDesign)

# CORRECT: Use an actual Model instance
mock_repo.get.return_value = ResearchDesignFactory.build(id=1)
```

**4. Datetime serialization in assert_success_response**
```python
# WRONG: Datetime serialization mismatches when comparing lists without model_dump
assert_success_response(response=response, expected_data=mock_items)

# CORRECT: Convert datetimes to ISO strings with model_dump(mode="json")
assert_success_response(
    response=response,
    expected_data=[item.model_dump(mode="json") for item in mock_items],
)
```

**5. None propagation failure in PATCH partial updates**
```python
# WRONG: The Factory default overrides None
mock_updated = ResearchDesignFactory.build()  # A default value is set for cohorts
# call_kwargs["cohorts"] is None → FAIL (the Factory default is present)

# CORRECT: Verify with call_args because the service parameter defaults to None
call_kwargs = mock_repo.update.call_args.kwargs
assert call_kwargs["cohorts"] is None  # Fields not provided are None
```

**6. Adding the async decorator**
```python
# Before
async def test_create_success(self, ...):

# After
@pytest.mark.asyncio
async def test_create_success(self, ...):
```

**7. Correcting the exception type**
```python
# Before - Generic Exception
with pytest.raises(Exception):

# After - Specific Exception
with pytest.raises(ResearchDesignNotFoundException):
```

## Output Format

```markdown
## Test Heal Report: {Feature}

### Review Summary
- Convention compliance: OK / (issues)
- Coverage: OK / (missing cases)
- Mock configuration: OK / (issues)

### Execution Result
- Total: {n} tests
- Passed: {n}
- Failed: {n}

### Failures Analysis
| Test | Error Type | Root Cause | Action |
|------|------------|------------|--------|
| test_xxx | AssertionError | Use build_response() instead of Factory.build() | Fixed |
| test_yyy | FixtureError | Missing fixture to retrieve service from mock_services | Fixed |

### Repairs Made
1. `test_create_success`: Factory.build() → Factory.build_response()
2. `test_get_not_found`: Added a fixture to retrieve a service from mock_services

### Implementation Issues (Reported)
1. `ResearchService.create`: The return type is not None - needs review

### Final Status
All tests passing / {n} tests still failing (implementation code changes required)
```

## Notes

- Fix only test code issues directly
- Report implementation code issues in detail for the developer to assess
- Always rerun tests after changes to confirm they pass
- Treat a test that fails identically more than three times as an implementation code issue
- **Before making changes, refer to passing tests in the same layer to understand the patterns**
