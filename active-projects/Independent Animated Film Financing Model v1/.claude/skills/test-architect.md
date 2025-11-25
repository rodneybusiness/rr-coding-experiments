# Test Architect Skill

You design and implement comprehensive test strategies for the Film Financing Navigator.

## Testing Stack
- **Backend**: pytest + pytest-cov
- **Frontend**: Jest + React Testing Library
- **Location**: Tests alongside source in `tests/` directories

## Test Organization Pattern

```python
# backend/tests/test_<module>.py

import pytest
from decimal import Decimal
from backend.models.<module> import <Model>

class Test<Model>:
    """Test <Model> functionality"""

    # === CREATION TESTS ===

    def test_valid_creation(self):
        """Test creating a valid <Model>"""
        model = <Model>(...)
        assert model.field == expected

    def test_invalid_<field>_rejected(self):
        """Test that invalid <field> raises ValueError"""
        with pytest.raises(ValueError, match="expected message"):
            <Model>(<field>=invalid_value)

    # === CALCULATION TESTS ===

    def test_<calculation>_basic(self):
        """Test basic <calculation>"""
        model = <Model>(...)
        result = model.<calculation>()
        assert result == expected

    def test_<calculation>_edge_case(self):
        """Test <calculation> with edge case"""
        # Zero values, max values, empty lists, etc.

    # === INTEGRATION TESTS ===

    def test_<model>_to_waterfall_node(self):
        """Test conversion to waterfall node"""
        model = <Model>(...)
        node = model.to_waterfall_node()
        assert node.priority == expected
```

## Required Test Categories

### 1. Model Validation Tests
- Valid inputs accepted
- Invalid inputs rejected with clear errors
- Boundary values (0, 100, max)
- Required vs optional fields

### 2. Calculation Tests
- Basic calculations correct
- Edge cases handled (division by zero, empty lists)
- Decimal precision maintained
- Negative scenarios

### 3. Integration Tests
- Model-to-model conversions work
- API endpoints return correct schemas
- Error responses are structured

### 4. Golden Scenario Tests
For engines, test against known-good scenarios:
```python
def test_golden_scenario_equity_deal(self):
    """Test scoring matches expected for standard equity deal"""
    deal = DealBlock(
        deal_type=DealType.EQUITY_INVESTMENT,
        ownership_percentage=Decimal("25"),
        # ... known inputs
    )
    result = scorer.score_scenario([deal])

    # Known expected outputs
    assert result.ownership_score >= Decimal("70")
    assert result.control_score >= Decimal("60")
```

## Test Coverage Requirements
- Core models: 95%+
- Engines: 90%+
- API endpoints: 85%+
- Frontend components: 70%+

## When Called
1. Analyze the component being tested
2. Identify test gaps
3. Generate comprehensive test suite
4. Include edge cases and golden scenarios
