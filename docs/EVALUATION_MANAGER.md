# Evaluation Manager Documentation

## Overview

The `EvaluationManager` is responsible for generating comprehensive interview assessments after a session is completed. It analyzes conversation history, whiteboard snapshots, and communication mode usage to produce structured feedback with competency scores, categorized feedback, and actionable improvement plans.

## Architecture

### Dependencies

- **Data Store**: Retrieves session data, conversation history, and media files
- **AI Interviewer**: Uses LLM capabilities for analysis and evaluation
- **Logger**: Logs all evaluation operations

### Key Components

1. **Competency Analysis**: Evaluates candidate performance across key system design competencies
2. **Feedback Categorization**: Organizes feedback into went_well, went_okay, and needs_improvement
3. **Communication Mode Analysis**: Assesses usage and effectiveness of audio, video, whiteboard, and screen share
4. **Improvement Plan Generation**: Creates actionable steps with resources for improvement
5. **Database Persistence**: Saves evaluation reports to database

## Usage

### Basic Usage

```python
from src.evaluation.evaluation_manager import EvaluationManager
from src.database.data_store import PostgresDataStore
from src.ai.ai_interviewer import AIInterviewer
from src.log_manager.logging_manager import LoggingManager

# Initialize dependencies
data_store = PostgresDataStore(...)
ai_interviewer = AIInterviewer(...)
logger = LoggingManager(...)

# Create evaluation manager
eval_manager = EvaluationManager(
    data_store=data_store,
    ai_interviewer=ai_interviewer,
    logger=logger
)

# Generate evaluation for a completed session
evaluation = eval_manager.generate_evaluation(session_id="session-123")

# Access evaluation components
print(f"Overall Score: {evaluation.overall_score}")
print(f"Competencies: {evaluation.competency_scores}")
print(f"Went Well: {evaluation.went_well}")
print(f"Needs Improvement: {evaluation.needs_improvement}")
print(f"Improvement Plan: {evaluation.improvement_plan}")
```

## Evaluation Process

### 1. Competency Analysis

The evaluation manager analyzes the conversation history to assess performance across key competencies:

- **Problem Decomposition**: Ability to break down complex problems
- **Scalability Considerations**: Understanding of scaling strategies
- **Reliability & Fault Tolerance**: Consideration of failure scenarios
- **Data Modeling**: Database and data structure design
- **Trade-off Analysis**: Evaluation of design alternatives
- **Communication Clarity**: Effectiveness of explanations
- **System Design Patterns**: Application of design patterns

Each competency receives:
- **Score**: 0-100 numeric score
- **Confidence Level**: high, medium, or low
- **Evidence**: Specific examples from the conversation

### 2. Feedback Categorization

Feedback is organized into three categories:

#### Went Well
Things the candidate did well (3-5 items)
- Clear descriptions
- Specific examples from conversation
- Positive reinforcement

#### Went Okay
Things that were acceptable but could be improved (2-4 items)
- Constructive observations
- Areas with room for growth
- Balanced feedback

#### Needs Improvement
Things that need significant improvement (2-4 items)
- Critical areas for development
- Specific gaps identified
- Actionable focus areas

### 3. Communication Mode Analysis

Analyzes usage and effectiveness of enabled communication modes:

- **Audio Quality**: Assessment of audio recordings
- **Video Presence**: Evaluation of video usage
- **Whiteboard Usage**: Analysis of diagram work
- **Screen Share Usage**: Assessment of screen sharing
- **Overall Communication**: Holistic communication effectiveness

### 4. Improvement Plan Generation

Creates a structured improvement plan with:

- **Priority Areas**: Top 3 lowest-scoring competencies
- **Concrete Steps**: Numbered action items with specific tasks
- **Resources**: Books, courses, and practice sites for each step
- **General Resources**: Additional learning materials

## Data Models

### EvaluationReport

```python
@dataclass
class EvaluationReport:
    session_id: str
    overall_score: float  # 0-100
    competency_scores: Dict[str, CompetencyScore]
    went_well: List[Feedback]
    went_okay: List[Feedback]
    needs_improvement: List[Feedback]
    improvement_plan: ImprovementPlan
    communication_mode_analysis: ModeAnalysis
    created_at: datetime
```

### CompetencyScore

```python
@dataclass
class CompetencyScore:
    score: float  # 0-100
    confidence_level: str  # "high", "medium", "low"
    evidence: List[str]  # Specific examples
```

### Feedback

```python
@dataclass
class Feedback:
    category: str  # "went_well", "went_okay", "needs_improvement"
    description: str
    evidence: List[str]  # Supporting examples
```

### ImprovementPlan

```python
@dataclass
class ImprovementPlan:
    priority_areas: List[str]
    concrete_steps: List[ActionItem]
    resources: List[str]

@dataclass
class ActionItem:
    step_number: int
    description: str
    resources: List[str]
```

### ModeAnalysis

```python
@dataclass
class ModeAnalysis:
    audio_quality: Optional[str]
    video_presence: Optional[str]
    whiteboard_usage: Optional[str]
    screen_share_usage: Optional[str]
    overall_communication: str
```

## Implementation Details

### LLM-Based Analysis

The evaluation manager uses the AI interviewer's LLM capabilities to:

1. **Analyze Competencies**: Sends conversation history to LLM with competency evaluation prompt
2. **Generate Feedback**: Requests categorized feedback based on conversation and scores
3. **Create Improvement Plan**: Generates actionable steps based on identified weaknesses

All LLM calls include:
- Retry logic with exponential backoff
- Token usage tracking
- Error handling
- Logging

### JSON Parsing

LLM responses are parsed as JSON with fallback handling:

```python
def _parse_competency_scores(self, response_content: str, competencies: List[str]):
    try:
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
        data = json.loads(json_match.group())
        # Parse competency scores...
    except Exception as e:
        # Return default scores if parsing fails
        return default_scores
```

### Database Persistence

Evaluations are automatically saved to the database:

```python
# Save evaluation to database
self.data_store.save_evaluation(evaluation)
```

The data store handles:
- JSON serialization of complex objects
- Upsert logic (insert or update)
- Transaction management

## Error Handling

### Exception Types

- **AIProviderError**: Raised when LLM analysis fails
- **ValueError**: Raised when session not found
- **DataStoreError**: Raised when database operations fail

### Retry Logic

LLM calls use retry logic with exponential backoff:
- Maximum 3 attempts
- Initial delay: 1 second
- Exponential backoff: 2x multiplier

### Fallback Behavior

If LLM parsing fails, the evaluation manager provides default values:
- Default competency scores (50.0 with low confidence)
- Basic feedback items
- Generic improvement plan

## Logging

All operations are logged with structured information:

```python
self.logger.info(
    component="EvaluationManager",
    operation="generate_evaluation",
    message="Evaluation generated successfully",
    session_id=session_id,
    metadata={
        "overall_score": overall_score,
        "competency_count": len(competency_scores),
    }
)
```

Log levels used:
- **INFO**: Successful operations, progress updates
- **WARNING**: Parsing failures, fallback usage
- **ERROR**: Critical failures, exceptions

## Performance Considerations

### Token Usage

Evaluation generation makes 3 LLM calls:
1. Competency analysis (~500-1000 tokens)
2. Feedback generation (~500-1000 tokens)
3. Improvement plan (~300-500 tokens)

Total estimated cost: $0.02-0.05 per evaluation (GPT-4)

### Processing Time

Typical evaluation generation:
- Competency analysis: 3-5 seconds
- Feedback generation: 3-5 seconds
- Improvement plan: 2-4 seconds
- Total: 8-14 seconds

### Optimization Tips

1. **Batch Processing**: Generate evaluations asynchronously
2. **Caching**: Cache common improvement resources
3. **Model Selection**: Use GPT-3.5 for faster/cheaper evaluations
4. **Prompt Optimization**: Refine prompts to reduce token usage

## Testing

### Unit Tests

Test individual methods:
- `_calculate_overall_score()`
- `_format_conversation()`
- `_parse_competency_scores()`
- `_parse_feedback()`
- `_parse_improvement_plan()`
- `_analyze_communication_modes()`

### Integration Tests

Test complete evaluation flow:
- Mock data store and AI interviewer
- Verify evaluation structure
- Check database persistence
- Validate error handling

### Example Test

```python
def test_generate_evaluation():
    # Setup mocks
    data_store = Mock()
    ai_interviewer = Mock()
    
    # Mock responses
    data_store.get_session.return_value = test_session
    data_store.get_conversation_history.return_value = test_messages
    ai_interviewer._call_llm_with_retry.return_value = (test_response, token_usage)
    
    # Generate evaluation
    manager = EvaluationManager(data_store, ai_interviewer)
    evaluation = manager.generate_evaluation("session-123")
    
    # Verify
    assert evaluation.overall_score > 0
    assert len(evaluation.competency_scores) > 0
    data_store.save_evaluation.assert_called_once()
```

## Requirements Mapping

The Evaluation Manager satisfies the following requirements:

- **Requirement 5.3**: Triggers evaluation generation when session ends
- **Requirement 6.1**: Generates evaluation report for completed sessions
- **Requirement 6.2**: Includes competency scores and confidence levels
- **Requirement 6.3**: Provides confidence level assessments
- **Requirement 6.4**: Categorizes feedback into three sections
- **Requirement 6.5**: Analyzes all enabled communication modes
- **Requirement 6.6**: Provides specific examples from responses
- **Requirement 6.7**: Includes actionable recommendations
- **Requirement 6.8**: Creates structured improvement plan with concrete steps
- **Requirement 6.9**: Saves evaluation to database

## Future Enhancements

### Potential Improvements

1. **Whiteboard Analysis**: Integrate vision LLM for diagram analysis
2. **Audio Analysis**: Analyze speech patterns and clarity
3. **Video Analysis**: Assess body language and engagement
4. **Comparative Analysis**: Compare performance across sessions
5. **Personalized Resources**: Recommend resources based on learning style
6. **Progress Tracking**: Track improvement over multiple sessions
7. **Peer Comparison**: Anonymous benchmarking against other candidates
8. **Custom Competencies**: Allow customizable competency frameworks

## Troubleshooting

### Common Issues

#### Issue: Evaluation generation fails

**Symptoms**: AIProviderError raised during evaluation

**Solutions**:
1. Check AI provider API key is valid
2. Verify network connectivity
3. Check token limits not exceeded
4. Review logs for specific error

#### Issue: Parsing errors in LLM responses

**Symptoms**: Warning logs about parsing failures

**Solutions**:
1. Review LLM response format
2. Adjust prompts for clearer JSON output
3. Increase temperature for more consistent formatting
4. Use fallback values (already implemented)

#### Issue: Low confidence scores

**Symptoms**: Many competencies marked as "low" confidence

**Solutions**:
1. Ensure sufficient conversation history
2. Check conversation quality and depth
3. Verify candidate provided detailed responses
4. Consider longer interview sessions

## Best Practices

1. **Generate After Session Completion**: Only generate evaluations for completed sessions
2. **Review Conversation Quality**: Ensure adequate conversation depth before evaluation
3. **Monitor Token Usage**: Track costs for evaluation generation
4. **Validate Results**: Spot-check evaluations for quality
5. **Iterate on Prompts**: Continuously improve evaluation prompts
6. **Handle Errors Gracefully**: Always provide fallback values
7. **Log Comprehensively**: Log all operations for debugging
8. **Test Thoroughly**: Test with various conversation scenarios

## Conclusion

The Evaluation Manager provides comprehensive, AI-powered interview assessments with structured feedback and actionable improvement plans. It integrates seamlessly with the interview platform's data store and AI interviewer components, providing valuable insights to help candidates improve their system design interview skills.
