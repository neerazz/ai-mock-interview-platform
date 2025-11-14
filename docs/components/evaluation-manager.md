# Evaluation Manager

The Evaluation Manager analyzes interview performance and generates comprehensive feedback reports.

## Overview

The Evaluation Manager:

- Analyzes conversation quality
- Evaluates system design approach
- Generates competency scores
- Creates personalized improvement plans

## Evaluation Criteria

### Problem Understanding (0-10)

- Clarifying questions asked
- Requirements gathering
- Constraint identification

### System Design Approach (0-10)

- High-level architecture
- Component breakdown
- Data flow design

### Communication Clarity (0-10)

- Explanation quality
- Thought process articulation
- Whiteboard usage

### Technical Depth (0-10)

- Technology choices
- Implementation details
- Edge case handling

### Trade-off Analysis (0-10)

- Alternative approaches considered
- Pros/cons discussed
- Justification quality

### Scalability Considerations (0-10)

- Performance optimization
- Bottleneck identification
- Scaling strategies

## Evaluation Report

```python
@dataclass
class Evaluation:
    session_id: str
    overall_score: float
    competency_scores: Dict[str, float]
    strengths: List[str]
    areas_for_improvement: List[str]
    improvement_plan: ImprovementPlan
    detailed_feedback: str
    created_at: datetime
```

## Improvement Plan

The improvement plan includes:

- Specific areas to focus on
- Concrete action steps
- Recommended resources
- Practice problems

## Usage Example

```python
# Generate evaluation
evaluation = evaluation_manager.evaluate_session(session_id)

# Access scores
print(f"Overall: {evaluation.overall_score}/10")
for competency, score in evaluation.competency_scores.items():
    print(f"{competency}: {score}/10")

# View improvement plan
for step in evaluation.improvement_plan.concrete_steps:
    print(f"- {step}")
```

## Related Components

- [Session Manager](session-manager.md)
- [AI Interviewer](ai-interviewer.md)
