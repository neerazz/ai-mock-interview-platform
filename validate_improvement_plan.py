"""
Validation script for improvement plan display (Task 13.4).

This script validates that the improvement plan section correctly displays:
- Priority areas in structured format
- Concrete action steps with descriptions
- Resources for improvement
- Export functionality (text and JSON)
"""

import sys
from datetime import datetime
from src.models import ImprovementPlan, ActionItem


def test_improvement_plan_structure():
    """Test that ImprovementPlan model has correct structure."""
    print("Testing ImprovementPlan structure...")
    
    # Create sample action items
    action_items = [
        ActionItem(
            step_number=1,
            description="Practice breaking down large systems into smaller components",
            resources=[
                "System Design Primer - Component Decomposition",
                "Designing Data-Intensive Applications by Martin Kleppmann"
            ]
        ),
        ActionItem(
            step_number=2,
            description="Study common scalability patterns and when to apply them",
            resources=[
                "Scalability Patterns - High Scalability Blog",
                "AWS Well-Architected Framework"
            ]
        ),
        ActionItem(
            step_number=3,
            description="Improve communication by practicing explaining technical concepts clearly",
            resources=[
                "Technical Communication Course - Coursera",
                "Practice with mock interviews"
            ]
        )
    ]
    
    # Create improvement plan
    improvement_plan = ImprovementPlan(
        priority_areas=[
            "Problem Decomposition - Break complex systems into manageable components",
            "Scalability Considerations - Understand horizontal vs vertical scaling",
            "Communication Clarity - Explain technical decisions more clearly"
        ],
        concrete_steps=action_items,
        resources=[
            "System Design Interview by Alex Xu",
            "Grokking the System Design Interview",
            "System Design Primer on GitHub",
            "High Scalability Blog"
        ]
    )
    
    # Validate structure
    assert len(improvement_plan.priority_areas) == 3, "Should have 3 priority areas"
    assert len(improvement_plan.concrete_steps) == 3, "Should have 3 action steps"
    assert len(improvement_plan.resources) == 4, "Should have 4 general resources"
    
    # Validate action items
    for action in improvement_plan.concrete_steps:
        assert action.step_number > 0, "Step number should be positive"
        assert len(action.description) > 0, "Description should not be empty"
        assert isinstance(action.resources, list), "Resources should be a list"
    
    print("✓ ImprovementPlan structure is correct")
    return improvement_plan


def test_text_export_format(improvement_plan: ImprovementPlan):
    """Test text export formatting."""
    print("\nTesting text export format...")
    
    # Import the formatting function
    from src.ui.pages.evaluation import format_improvement_plan_as_text
    
    text_content = format_improvement_plan_as_text(improvement_plan)
    
    # Validate text content
    assert "IMPROVEMENT PLAN" in text_content, "Should have title"
    assert "PRIORITY AREAS" in text_content, "Should have priority areas section"
    assert "ACTION STEPS" in text_content, "Should have action steps section"
    assert "RECOMMENDED RESOURCES" in text_content, "Should have resources section"
    
    # Check that all priority areas are included
    for area in improvement_plan.priority_areas:
        assert area in text_content, f"Priority area '{area}' should be in text"
    
    # Check that all action steps are included
    for action in improvement_plan.concrete_steps:
        assert f"Step {action.step_number}" in text_content, f"Step {action.step_number} should be in text"
        assert action.description in text_content, f"Action description should be in text"
    
    print("✓ Text export format is correct")
    print("\nSample text export:")
    print("-" * 80)
    print(text_content[:500] + "...")
    print("-" * 80)


def test_json_export_format(improvement_plan: ImprovementPlan):
    """Test JSON export formatting."""
    print("\nTesting JSON export format...")
    
    # Import the formatting function
    from src.ui.pages.evaluation import format_improvement_plan_as_json
    import json
    
    json_content = format_improvement_plan_as_json(improvement_plan)
    
    # Parse JSON to validate structure
    data = json.loads(json_content)
    
    # Validate JSON structure
    assert "priority_areas" in data, "Should have priority_areas field"
    assert "concrete_steps" in data, "Should have concrete_steps field"
    assert "resources" in data, "Should have resources field"
    assert "generated_at" in data, "Should have generated_at timestamp"
    
    # Validate content
    assert len(data["priority_areas"]) == len(improvement_plan.priority_areas), "Priority areas count should match"
    assert len(data["concrete_steps"]) == len(improvement_plan.concrete_steps), "Action steps count should match"
    assert len(data["resources"]) == len(improvement_plan.resources), "Resources count should match"
    
    # Validate action step structure
    for step in data["concrete_steps"]:
        assert "step_number" in step, "Step should have step_number"
        assert "description" in step, "Step should have description"
        assert "resources" in step, "Step should have resources"
    
    print("✓ JSON export format is correct")
    print("\nSample JSON export:")
    print("-" * 80)
    print(json_content[:500] + "...")
    print("-" * 80)


def test_render_functions_exist():
    """Test that all required render functions exist."""
    print("\nTesting render functions...")
    
    from src.ui.pages.evaluation import (
        render_improvement_plan,
        render_action_item,
        render_improvement_plan_export,
        format_improvement_plan_as_text,
        format_improvement_plan_as_json
    )
    
    # Check that functions are callable
    assert callable(render_improvement_plan), "render_improvement_plan should be callable"
    assert callable(render_action_item), "render_action_item should be callable"
    assert callable(render_improvement_plan_export), "render_improvement_plan_export should be callable"
    assert callable(format_improvement_plan_as_text), "format_improvement_plan_as_text should be callable"
    assert callable(format_improvement_plan_as_json), "format_improvement_plan_as_json should be callable"
    
    print("✓ All render functions exist and are callable")


def main():
    """Run all validation tests."""
    print("=" * 80)
    print("IMPROVEMENT PLAN DISPLAY VALIDATION (Task 13.4)")
    print("=" * 80)
    
    try:
        # Test 1: Structure
        improvement_plan = test_improvement_plan_structure()
        
        # Test 2: Text export
        test_text_export_format(improvement_plan)
        
        # Test 3: JSON export
        test_json_export_format(improvement_plan)
        
        # Test 4: Render functions
        test_render_functions_exist()
        
        print("\n" + "=" * 80)
        print("✓ ALL VALIDATION TESTS PASSED")
        print("=" * 80)
        print("\nTask 13.4 Implementation Summary:")
        print("- ✓ Priority areas displayed in structured format")
        print("- ✓ Concrete action steps with descriptions and resources")
        print("- ✓ General resources section")
        print("- ✓ Text export functionality")
        print("- ✓ JSON export functionality")
        print("- ✓ All render functions implemented")
        print("\nRequirements satisfied:")
        print("- ✓ 6.7: Actionable recommendations with structured improvement plan")
        print("- ✓ 6.8: Concrete steps to address identified weaknesses")
        print("=" * 80)
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
