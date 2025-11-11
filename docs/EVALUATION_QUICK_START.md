# Evaluation Manager Quick Start Guide

## Basic Usage

### 1. Initialize the Evaluation Manager

```python
from src.evaluation.evaluation_manager import EvaluationManager
from src.database.data_store import PostgresDataStore
from src.ai.ai_interviewer import AIInterviewer
from src.ai.token_tracker import TokenTracker
from src.log_manager.logging_manager import LoggingManager

# Setup dependencies
data_store = PostgresDataStore(
    host="localhost",
    port=5432,
    database="interview_platform",
    user="interview_user",
    password="your_password"
)

token_tracker = TokenTracker(data_store=data_store)

ai_interviewer = AIInterviewer(
    provider="openai",
    model="gpt-4",
    api_key="your_api_key",
    token_tracker=token_tracker
)

logger = LoggingManager(config=logging_config)

# Create evaluation manager
eval_manager = EvaluationManager(
    data_store=data_store,
    ai_interviewer=ai_interviewer,
    logger=logger
)
```

### 2. Generate Evaluation

```python
# Generate evaluation for a completed session
evaluation = eval_manager.generate_evaluation(session_id="session-123")
```

### 3. Access Evaluation Results

```python
# Overall score
print(f"Overall Score: {evaluation.overall_score}/100")

# Competency scores
for competency, score in evaluation.competency_scores.items():
    print(f"{competency}: {score.score}/100 ({score.confidence_level} confidence)")
    print(f"  Evidence: {', '.join(score.evidence)}")

# Feedback categories
print("\n✓ Went Well:")
for feedback in evaluation.went_well:
    print(f"  - {feedback.description}")

print("\n⚠ Went Okay:")
for feedback in evaluation.went_okay:
    print(f"  - {feedback.description}")

print("\n✗ Needs Improvement:")
for feedback in evaluation.needs_improvement:
    print(f"  - {feedback.description}")

# Improvement plan
print("\nImprovement Plan:")
print(f"Priority Areas: {', '.join(evaluation.improvement_plan.priority_areas)}")
for step in evaluation.improvement_plan.concrete_steps:
    print(f"{step.step_number}. {step.description}")
    print(f"   Resources: {', '.join(step.resources)}")

# Communication mode analysis
print("\nCommunication Analysis:")
print(f"Audio: {evaluation.communication_mode_analysis.audio_quality}")
print(f"Video: {evaluation.communication_mode_analysis.video_presence}")
print(f"Whiteboard: {evaluation.communication_mode_analysis.whiteboard_usage}")
print(f"Overall: {evaluation.communication_mode_analysis.overall_communication}")
```

## Integration with Session Manager

```python
class SessionManager:
    def end_session(self, session_id: str) -> EvaluationReport:
        """End session and generate evaluation."""
        # Update session status
        session = self.data_store.get_session(session_id)
        session.status = SessionStatus.COMPLETED
        session.ended_at = datetime.now()
        self.data_store.save_session(session)
        
        # Generate evaluation
        evaluation = self.eval_manager.generate_evaluation(session_id)
        
        return evaluation
```

## Retrieving Saved Evaluations

```python
# Retrieve evaluation from database
evaluation = data_store.get_evaluation(session_id="session-123")

if evaluation:
    print(f"Evaluation created at: {evaluation.created_at}")
    print(f"Overall score: {evaluation.overall_score}")
else:
    print("No evaluation found for this session")
```

## Error Handling

```python
from src.exceptions import AIProviderError

try:
    evaluation = eval_manager.generate_evaluation(session_id)
except AIProviderError as e:
    print(f"Evaluation generation failed: {e}")
    # Handle error (retry, notify user, etc.)
except ValueError as e:
    print(f"Session not found: {e}")
```

## Customizing Evaluation

### Using Different AI Models

```python
# Use GPT-3.5 for faster/cheaper evaluations
ai_interviewer = AIInterviewer(
    provider="openai",
    model="gpt-3.5-turbo",
    api_key="your_api_key",
    token_tracker=token_tracker,
    temperature=0.7  # Adjust for consistency
)

# Use Claude for alternative perspective
ai_interviewer = AIInterviewer(
    provider="anthropic",
    model="claude-3-sonnet-20240229",
    api_key="your_api_key",
    token_tracker=token_tracker
)
```

## Monitoring and Logging

```python
# Check logs for evaluation operations
logs = data_store.get_audit_logs(
    component="EvaluationManager",
    session_id=session_id
)

for log in logs:
    print(f"[{log.level}] {log.operation}: {log.message}")
```

## Performance Tips

### 1. Async Evaluation Generation

```python
import asyncio

async def generate_evaluation_async(session_id: str):
    """Generate evaluation asynchronously."""
    loop = asyncio.get_event_loop()
    evaluation = await loop.run_in_executor(
        None, 
        eval_manager.generate_evaluation, 
        session_id
    )
    return evaluation

# Use in async context
evaluation = await generate_evaluation_async("session-123")
```

### 2. Batch Processing

```python
def generate_evaluations_batch(session_ids: List[str]):
    """Generate evaluations for multiple sessions."""
    evaluations = []
    for session_id in session_ids:
        try:
            evaluation = eval_manager.generate_evaluation(session_id)
            evaluations.append(evaluation)
        except Exception as e:
            print(f"Failed to generate evaluation for {session_id}: {e}")
    return evaluations
```

### 3. Token Usage Monitoring

```python
# Check token usage for evaluation
token_usage = data_store.get_token_usage(session_id)
evaluation_tokens = [
    t for t in token_usage 
    if t.operation in ["analyze_competencies", "generate_feedback", "generate_improvement_plan"]
]

total_cost = sum(t.estimated_cost for t in evaluation_tokens)
print(f"Evaluation cost: ${total_cost:.4f}")
```

## Common Patterns

### Pattern 1: Evaluation with Notification

```python
def generate_and_notify(session_id: str, user_email: str):
    """Generate evaluation and send notification."""
    evaluation = eval_manager.generate_evaluation(session_id)
    
    # Send email notification
    send_email(
        to=user_email,
        subject="Your Interview Evaluation is Ready",
        body=f"Overall Score: {evaluation.overall_score}/100"
    )
    
    return evaluation
```

### Pattern 2: Evaluation with Comparison

```python
def generate_with_comparison(session_id: str, user_id: str):
    """Generate evaluation and compare with previous sessions."""
    evaluation = eval_manager.generate_evaluation(session_id)
    
    # Get previous sessions
    previous_sessions = data_store.list_sessions(user_id=user_id)
    previous_scores = [
        data_store.get_evaluation(s.id).overall_score 
        for s in previous_sessions[1:]  # Skip current session
        if data_store.get_evaluation(s.id)
    ]
    
    if previous_scores:
        avg_previous = sum(previous_scores) / len(previous_scores)
        improvement = evaluation.overall_score - avg_previous
        print(f"Improvement: {improvement:+.1f} points")
    
    return evaluation
```

### Pattern 3: Evaluation with Export

```python
import json

def generate_and_export(session_id: str, output_file: str):
    """Generate evaluation and export to JSON."""
    evaluation = eval_manager.generate_evaluation(session_id)
    
    # Convert to dict for JSON serialization
    eval_dict = {
        "session_id": evaluation.session_id,
        "overall_score": evaluation.overall_score,
        "competency_scores": {
            name: {
                "score": score.score,
                "confidence": score.confidence_level,
                "evidence": score.evidence
            }
            for name, score in evaluation.competency_scores.items()
        },
        "went_well": [
            {"description": f.description, "evidence": f.evidence}
            for f in evaluation.went_well
        ],
        "needs_improvement": [
            {"description": f.description, "evidence": f.evidence}
            for f in evaluation.needs_improvement
        ],
        "improvement_plan": {
            "priority_areas": evaluation.improvement_plan.priority_areas,
            "steps": [
                {
                    "number": step.step_number,
                    "description": step.description,
                    "resources": step.resources
                }
                for step in evaluation.improvement_plan.concrete_steps
            ]
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(eval_dict, f, indent=2)
    
    return evaluation
```

## Troubleshooting

### Issue: Evaluation takes too long

**Solution**: Use GPT-3.5 instead of GPT-4
```python
ai_interviewer = AIInterviewer(
    provider="openai",
    model="gpt-3.5-turbo",  # Faster than GPT-4
    api_key="your_api_key",
    token_tracker=token_tracker
)
```

### Issue: Parsing errors in LLM responses

**Solution**: Check logs and adjust temperature
```python
ai_interviewer = AIInterviewer(
    provider="openai",
    model="gpt-4",
    api_key="your_api_key",
    token_tracker=token_tracker,
    temperature=0.3  # Lower temperature for more consistent JSON
)
```

### Issue: Low confidence scores

**Solution**: Ensure adequate conversation depth
```python
# Check conversation length
conversation = data_store.get_conversation_history(session_id)
if len(conversation) < 10:
    print("Warning: Short conversation may result in low confidence scores")
```

## Best Practices

1. **Always check session status** before generating evaluation
2. **Handle errors gracefully** with try-except blocks
3. **Monitor token usage** to control costs
4. **Log all operations** for debugging
5. **Validate session data** before evaluation
6. **Use async processing** for better performance
7. **Cache common resources** to reduce redundancy
8. **Test with various scenarios** to ensure quality

## Next Steps

- Integrate with Session Manager (Task 10)
- Display evaluations in Streamlit UI (Task 13)
- Add comprehensive tests (Task 20)
- Implement progress tracking across sessions
- Add custom competency frameworks
- Integrate whiteboard vision analysis

---

For detailed documentation, see [EVALUATION_MANAGER.md](./EVALUATION_MANAGER.md)
