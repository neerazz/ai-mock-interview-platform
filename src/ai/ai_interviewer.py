"""
AI Interviewer Agent for conducting system design interviews.

This module provides the AIInterviewer class that uses LangChain to conduct
interviews, generate questions, analyze responses, and provide follow-ups.
"""

import time
from typing import Optional, Dict, Any, List
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from src.models import (
    ResumeData,
    InterviewResponse,
    TokenUsage,
    WhiteboardAnalysis,
    ConversationContext,
    Message,
)
from src.ai.token_tracker import TokenTracker
from src.exceptions import AIProviderError


# System prompt for system design interviews
SYSTEM_DESIGN_PROMPT = """You are an expert technical interviewer conducting a system design interview. 
Your role is to:
1. Ask thoughtful, probing questions about system architecture and design
2. Evaluate the candidate's understanding of scalability, reliability, and trade-offs
3. Provide constructive follow-up questions based on their responses
4. Adapt the difficulty based on the candidate's experience level
5. Focus on real-world scenarios and practical considerations

Guidelines:
- Be professional and encouraging
- Ask one question at a time
- Listen carefully to responses before asking follow-ups
- Cover key topics: scalability, reliability, data consistency, trade-offs, monitoring
- Ask clarifying questions when responses are ambiguous
- Probe deeper into design decisions and their implications

Remember: You are evaluating their thought process, not just the final solution."""


class AIInterviewer:
    """
    AI-powered interviewer agent for system design interviews.
    
    Uses LangChain to manage conversation flow, generate questions,
    analyze responses, and provide contextual follow-ups. Supports
    multiple AI providers (OpenAI, Anthropic) with token tracking.
    
    Attributes:
        provider: AI provider name (openai or anthropic)
        model: Model name
        llm: LangChain LLM instance
        memory: Conversation memory
        token_tracker: Token usage tracker
        logger: Optional logging manager
        resume_data: Optional resume data for context
    """

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        token_tracker: TokenTracker,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        logger=None,
    ):
        """
        Initialize AI Interviewer with provider configuration.
        
        Args:
            provider: AI provider name (openai or anthropic)
            model: Model name
            api_key: API key for the provider
            token_tracker: TokenTracker instance for usage monitoring
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens per response
            logger: Optional LoggingManager instance
            
        Raises:
            AIProviderError: If provider initialization fails
        """
        self.provider = provider.lower()
        self.model = model
        self.token_tracker = token_tracker
        self.logger = logger
        self.resume_data: Optional[ResumeData] = None
        self.session_id: Optional[str] = None

        if self.logger:
            self.logger.info(
                component="AIInterviewer",
                operation="__init__",
                message=f"Initializing AI Interviewer with {provider}/{model}",
                metadata={
                    "provider": provider,
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

        try:
            # Initialize LLM based on provider
            if self.provider == "openai":
                self.llm = ChatOpenAI(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=api_key,
                )
            elif self.provider == "anthropic":
                self.llm = ChatAnthropic(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=api_key,
                )
            else:
                raise AIProviderError(f"Unsupported AI provider: {provider}")

            # Initialize conversation memory
            self.memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
            )

            if self.logger:
                self.logger.info(
                    component="AIInterviewer",
                    operation="__init__",
                    message="AI Interviewer initialized successfully",
                )

        except Exception as e:
            error_msg = f"Failed to initialize AI Interviewer: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="AIInterviewer",
                    operation="__init__",
                    message=error_msg,
                    exc_info=e,
                )
            raise AIProviderError(error_msg) from e

    def initialize(
        self, session_id: str, resume_data: Optional[ResumeData] = None
    ) -> None:
        """
        Initialize interviewer for a new session.
        
        Args:
            session_id: Session identifier
            resume_data: Optional resume data for context-aware questions
        """
        self.session_id = session_id
        self.resume_data = resume_data
        self.memory.clear()

        if self.logger:
            self.logger.info(
                component="AIInterviewer",
                operation="initialize",
                message=f"Initialized interviewer for session {session_id}",
                session_id=session_id,
                metadata={
                    "has_resume": resume_data is not None,
                    "experience_level": resume_data.experience_level
                    if resume_data
                    else None,
                },
            )

    def start_interview(self) -> InterviewResponse:
        """
        Start the interview with an opening question.
        
        Generates an initial problem statement based on resume data if available,
        otherwise generates a general system design problem.
        
        Returns:
            InterviewResponse with opening question and token usage
            
        Raises:
            AIProviderError: If question generation fails
        """
        if self.logger:
            self.logger.info(
                component="AIInterviewer",
                operation="start_interview",
                message="Starting interview",
                session_id=self.session_id,
            )

        try:
            # Generate problem based on resume if available
            if self.resume_data:
                problem = self.generate_problem(self.resume_data)
            else:
                problem = self._generate_default_problem()

            # Create opening message
            opening_message = f"""Welcome to your system design interview! 

Here's the problem we'll be working on today:

{problem}

Take a moment to think about the problem. When you're ready, please start by clarifying any requirements or constraints you'd like to understand better."""

            # Track as system message (no tokens for this)
            token_usage = TokenUsage(
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                estimated_cost=0.0,
                provider=self.provider,
                model=self.model,
                operation="start_interview",
            )

            # Add to memory
            self.memory.chat_memory.add_ai_message(opening_message)

            if self.logger:
                self.logger.info(
                    component="AIInterviewer",
                    operation="start_interview",
                    message="Interview started successfully",
                    session_id=self.session_id,
                )

            return InterviewResponse(content=opening_message, token_usage=token_usage)

        except Exception as e:
            error_msg = f"Failed to start interview: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="AIInterviewer",
                    operation="start_interview",
                    message=error_msg,
                    session_id=self.session_id,
                    exc_info=e,
                )
            raise AIProviderError(error_msg) from e

    def _generate_default_problem(self) -> str:
        """
        Generate a default system design problem.
        
        Returns:
            Problem statement string
        """
        return """Design a URL shortening service like bit.ly.

The service should:
- Accept long URLs and return short URLs
- Redirect users from short URLs to original long URLs
- Handle high traffic (millions of requests per day)
- Track click analytics for each short URL

Consider scalability, reliability, and performance in your design."""

    def _call_llm_with_retry(
        self, messages: List[Any], operation: str, max_retries: int = 3
    ) -> tuple[str, TokenUsage]:
        """
        Call LLM API with retry logic and token tracking.
        
        Args:
            messages: List of messages to send
            operation: Operation name for tracking
            max_retries: Maximum number of retry attempts
            
        Returns:
            Tuple of (response_content, token_usage)
            
        Raises:
            AIProviderError: If all retry attempts fail
        """
        retry_delay = 1  # Start with 1 second delay

        for attempt in range(max_retries):
            try:
                start_time = time.time()

                # Call LLM
                response = self.llm.invoke(messages)
                
                duration_ms = (time.time() - start_time) * 1000

                # Extract token usage from response
                input_tokens = 0
                output_tokens = 0

                if hasattr(response, "response_metadata"):
                    metadata = response.response_metadata
                    if "token_usage" in metadata:
                        usage = metadata["token_usage"]
                        input_tokens = usage.get("prompt_tokens", 0)
                        output_tokens = usage.get("completion_tokens", 0)
                    elif "usage" in metadata:
                        usage = metadata["usage"]
                        input_tokens = usage.get("input_tokens", 0)
                        output_tokens = usage.get("output_tokens", 0)

                # Create token usage record
                token_usage = self.token_tracker.record_usage(
                    session_id=self.session_id,
                    provider=self.provider,
                    model=self.model,
                    operation=operation,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )

                if self.logger:
                    self.logger.info(
                        component="AIInterviewer",
                        operation=operation,
                        message=f"LLM call completed in {duration_ms:.2f}ms",
                        session_id=self.session_id,
                        metadata={
                            "duration_ms": duration_ms,
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "estimated_cost": token_usage.estimated_cost,
                        },
                    )

                return response.content, token_usage

            except Exception as e:
                if self.logger:
                    self.logger.warning(
                        component="AIInterviewer",
                        operation=operation,
                        message=f"LLM call attempt {attempt + 1} failed: {str(e)}",
                        session_id=self.session_id,
                        metadata={"attempt": attempt + 1, "error": str(e)},
                    )

                if attempt < max_retries - 1:
                    # Exponential backoff
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    # Final attempt failed
                    error_msg = f"LLM call failed after {max_retries} attempts: {str(e)}"
                    if self.logger:
                        self.logger.error(
                            component="AIInterviewer",
                            operation=operation,
                            message=error_msg,
                            session_id=self.session_id,
                            exc_info=e,
                        )
                    raise AIProviderError(error_msg) from e

    def process_response(
        self,
        candidate_response: str,
        whiteboard_image: Optional[bytes] = None,
    ) -> InterviewResponse:
        """
        Process candidate response and generate follow-up question.
        
        Analyzes the candidate's response for completeness and clarity,
        then generates a contextually relevant follow-up question.
        
        Args:
            candidate_response: Candidate's text response
            whiteboard_image: Optional whiteboard image for analysis
            
        Returns:
            InterviewResponse with follow-up question and token usage
            
        Raises:
            AIProviderError: If response processing fails
        """
        if self.logger:
            self.logger.info(
                component="AIInterviewer",
                operation="process_response",
                message="Processing candidate response",
                session_id=self.session_id,
                metadata={"response_length": len(candidate_response)},
            )

        try:
            # Add candidate response to memory
            self.memory.chat_memory.add_user_message(candidate_response)

            # Build context for follow-up
            messages = [
                SystemMessage(content=SYSTEM_DESIGN_PROMPT),
            ]

            # Add conversation history
            for msg in self.memory.chat_memory.messages:
                messages.append(msg)

            # Add instruction for follow-up
            messages.append(
                SystemMessage(
                    content="""Based on the candidate's response, generate a thoughtful follow-up question that:
1. Probes deeper into their design decisions
2. Explores trade-offs and alternatives
3. Covers important system design topics (scalability, reliability, consistency, etc.)
4. Asks for clarification if the response was ambiguous

Keep your question focused and specific. Ask only ONE question."""
                )
            )

            # Call LLM with retry
            response_content, token_usage = self._call_llm_with_retry(
                messages, operation="process_response"
            )

            # Add AI response to memory
            self.memory.chat_memory.add_ai_message(response_content)

            if self.logger:
                self.logger.info(
                    component="AIInterviewer",
                    operation="process_response",
                    message="Response processed successfully",
                    session_id=self.session_id,
                )

            return InterviewResponse(content=response_content, token_usage=token_usage)

        except Exception as e:
            error_msg = f"Failed to process response: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="AIInterviewer",
                    operation="process_response",
                    message=error_msg,
                    session_id=self.session_id,
                    exc_info=e,
                )
            raise AIProviderError(error_msg) from e

    def generate_followup(self, context: ConversationContext) -> InterviewResponse:
        """
        Generate a follow-up question based on conversation context.
        
        Args:
            context: Conversation context with messages and metadata
            
        Returns:
            InterviewResponse with follow-up question and token usage
            
        Raises:
            AIProviderError: If follow-up generation fails
        """
        if self.logger:
            self.logger.info(
                component="AIInterviewer",
                operation="generate_followup",
                message="Generating follow-up question",
                session_id=self.session_id,
            )

        try:
            # Build messages from context
            messages = [SystemMessage(content=SYSTEM_DESIGN_PROMPT)]

            for msg in context.messages:
                if msg.role == "candidate":
                    messages.append(HumanMessage(content=msg.content))
                else:
                    messages.append(AIMessage(content=msg.content))

            # Add follow-up instruction
            messages.append(
                SystemMessage(
                    content="Generate a relevant follow-up question to continue the interview."
                )
            )

            # Call LLM with retry
            response_content, token_usage = self._call_llm_with_retry(
                messages, operation="generate_followup"
            )

            return InterviewResponse(content=response_content, token_usage=token_usage)

        except Exception as e:
            error_msg = f"Failed to generate follow-up: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="AIInterviewer",
                    operation="generate_followup",
                    message=error_msg,
                    session_id=self.session_id,
                    exc_info=e,
                )
            raise AIProviderError(error_msg) from e


    def generate_problem(self, resume_data: ResumeData) -> str:
        """
        Generate a system design problem tailored to candidate's resume.
        
        Considers experience level, domain expertise, and years of experience
        to create an appropriately challenging problem.
        
        Args:
            resume_data: Candidate's resume data
            
        Returns:
            Problem statement string
            
        Raises:
            AIProviderError: If problem generation fails
        """
        if self.logger:
            self.logger.info(
                component="AIInterviewer",
                operation="generate_problem",
                message="Generating resume-aware problem",
                session_id=self.session_id,
                metadata={
                    "experience_level": resume_data.experience_level,
                    "years_of_experience": resume_data.years_of_experience,
                    "domain_expertise": resume_data.domain_expertise,
                },
            )

        try:
            # Build prompt for problem generation
            prompt = f"""Generate a system design interview problem for a candidate with the following background:

Experience Level: {resume_data.experience_level}
Years of Experience: {resume_data.years_of_experience}
Domain Expertise: {', '.join(resume_data.domain_expertise)}
Recent Role: {resume_data.work_experience[0].title if resume_data.work_experience else 'N/A'}

The problem should:
1. Match their experience level:
   - Junior (0-2 years): Focus on basic system components and simple scaling
   - Mid (3-5 years): Include distributed systems concepts and trade-offs
   - Senior (6-10 years): Complex systems with multiple services and data consistency
   - Staff (10+ years): Large-scale systems with organizational and technical challenges

2. Relate to their domain expertise when possible
3. Be appropriate for a 45-minute interview
4. Cover key system design concepts (scalability, reliability, data modeling, trade-offs)
5. Be realistic and based on real-world scenarios

Generate ONLY the problem statement. Be specific about requirements and constraints."""

            messages = [
                SystemMessage(content="You are an expert technical interviewer."),
                HumanMessage(content=prompt),
            ]

            # Call LLM with retry
            problem_statement, token_usage = self._call_llm_with_retry(
                messages, operation="generate_problem"
            )

            if self.logger:
                self.logger.info(
                    component="AIInterviewer",
                    operation="generate_problem",
                    message="Problem generated successfully",
                    session_id=self.session_id,
                )

            return problem_statement

        except Exception as e:
            error_msg = f"Failed to generate problem: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="AIInterviewer",
                    operation="generate_problem",
                    message=error_msg,
                    session_id=self.session_id,
                    exc_info=e,
                )
            raise AIProviderError(error_msg) from e

    def analyze_whiteboard(self, whiteboard_image: bytes) -> WhiteboardAnalysis:
        """
        Analyze whiteboard diagram using vision-enabled LLM.
        
        Identifies components, relationships, missing elements, and design patterns
        in the system diagram.
        
        Args:
            whiteboard_image: Whiteboard image as bytes
            
        Returns:
            WhiteboardAnalysis with identified elements
            
        Raises:
            AIProviderError: If whiteboard analysis fails
        """
        if self.logger:
            self.logger.info(
                component="AIInterviewer",
                operation="analyze_whiteboard",
                message="Analyzing whiteboard diagram",
                session_id=self.session_id,
                metadata={"image_size_bytes": len(whiteboard_image)},
            )

        try:
            # For now, return a placeholder since vision API requires special handling
            # This would need to be implemented with proper vision model support
            if self.logger:
                self.logger.warning(
                    component="AIInterviewer",
                    operation="analyze_whiteboard",
                    message="Whiteboard analysis not yet implemented - returning placeholder",
                    session_id=self.session_id,
                )

            # Placeholder implementation
            # In production, this would use GPT-4 Vision or Claude 3 with vision capabilities
            return WhiteboardAnalysis(
                components_identified=[
                    "Load Balancer",
                    "Application Servers",
                    "Database",
                    "Cache Layer",
                ],
                relationships=[
                    "Load Balancer -> Application Servers",
                    "Application Servers -> Cache Layer",
                    "Application Servers -> Database",
                ],
                missing_elements=[
                    "Message Queue for async processing",
                    "CDN for static content",
                    "Monitoring and alerting system",
                ],
                design_patterns=["Load Balancing", "Caching", "Database Replication"],
            )

        except Exception as e:
            error_msg = f"Failed to analyze whiteboard: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="AIInterviewer",
                    operation="analyze_whiteboard",
                    message=error_msg,
                    session_id=self.session_id,
                    exc_info=e,
                )
            raise AIProviderError(error_msg) from e

    def ask_clarifying_question(self, ambiguous_response: str) -> InterviewResponse:
        """
        Generate a clarifying question for an ambiguous response.
        
        Args:
            ambiguous_response: The candidate's ambiguous response
            
        Returns:
            InterviewResponse with clarifying question and token usage
            
        Raises:
            AIProviderError: If question generation fails
        """
        if self.logger:
            self.logger.info(
                component="AIInterviewer",
                operation="ask_clarifying_question",
                message="Generating clarifying question",
                session_id=self.session_id,
            )

        try:
            messages = [
                SystemMessage(content=SYSTEM_DESIGN_PROMPT),
                HumanMessage(
                    content=f"""The candidate gave this response:

"{ambiguous_response}"

This response is unclear or incomplete. Generate a polite clarifying question that:
1. Points out what's unclear or missing
2. Asks for specific details or elaboration
3. Helps the candidate provide a more complete answer

Be constructive and encouraging."""
                ),
            ]

            # Call LLM with retry
            response_content, token_usage = self._call_llm_with_retry(
                messages, operation="ask_clarifying_question"
            )

            # Add to memory
            self.memory.chat_memory.add_ai_message(response_content)

            if self.logger:
                self.logger.info(
                    component="AIInterviewer",
                    operation="ask_clarifying_question",
                    message="Clarifying question generated",
                    session_id=self.session_id,
                )

            return InterviewResponse(content=response_content, token_usage=token_usage)

        except Exception as e:
            error_msg = f"Failed to generate clarifying question: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="AIInterviewer",
                    operation="ask_clarifying_question",
                    message=error_msg,
                    session_id=self.session_id,
                    exc_info=e,
                )
            raise AIProviderError(error_msg) from e

    def adapt_difficulty(self, performance_indicators: Dict[str, Any]) -> None:
        """
        Adapt question difficulty based on candidate performance.
        
        Adjusts the interviewer's approach based on how well the candidate
        is performing. This affects future question generation.
        
        Args:
            performance_indicators: Dictionary with performance metrics
                - response_quality: "high", "medium", "low"
                - depth_of_understanding: "deep", "moderate", "shallow"
                - technical_accuracy: "accurate", "mostly_accurate", "inaccurate"
        """
        if self.logger:
            self.logger.info(
                component="AIInterviewer",
                operation="adapt_difficulty",
                message="Adapting difficulty based on performance",
                session_id=self.session_id,
                metadata=performance_indicators,
            )

        # Add performance context to memory for future questions
        performance_summary = f"""Performance indicators:
- Response Quality: {performance_indicators.get('response_quality', 'unknown')}
- Depth of Understanding: {performance_indicators.get('depth_of_understanding', 'unknown')}
- Technical Accuracy: {performance_indicators.get('technical_accuracy', 'unknown')}

Adjust your questions accordingly - make them more challenging if performance is high, 
or more supportive and guiding if the candidate is struggling."""

        self.memory.chat_memory.add_message(
            SystemMessage(content=performance_summary)
        )

        if self.logger:
            self.logger.info(
                component="AIInterviewer",
                operation="adapt_difficulty",
                message="Difficulty adapted",
                session_id=self.session_id,
            )

    def get_conversation_history(self) -> List[Message]:
        """
        Get the conversation history from memory.
        
        Returns:
            List of Message objects representing the conversation
        """
        messages = []
        for msg in self.memory.chat_memory.messages:
            if isinstance(msg, HumanMessage):
                role = "candidate"
            elif isinstance(msg, AIMessage):
                role = "interviewer"
            else:
                role = "system"

            messages.append(
                Message(
                    role=role,
                    content=msg.content,
                    timestamp=datetime.now(),
                    metadata={},
                )
            )

        return messages

    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.memory.clear()
        if self.logger:
            self.logger.info(
                component="AIInterviewer",
                operation="clear_memory",
                message="Conversation memory cleared",
                session_id=self.session_id,
            )
