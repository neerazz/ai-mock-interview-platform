"""
Evaluation Manager for generating comprehensive interview assessments.

This module provides the EvaluationManager class that analyzes interview sessions
across all communication modes and generates structured feedback with improvement plans.
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_core.messages import SystemMessage, HumanMessage

from src.models import (
    EvaluationReport,
    CompetencyScore,
    Feedback,
    ImprovementPlan,
    ActionItem,
    ModeAnalysis,
    Message,
    MediaFile,
    CommunicationMode,
)
from src.exceptions import AIProviderError


class EvaluationManager:
    """
    Evaluation manager for generating comprehensive interview assessments.
    
    Analyzes conversation history, whiteboard snapshots, and communication modes
    to generate structured feedback with competency scores, categorized feedback,
    and actionable improvement plans.
    
    Attributes:
        data_store: IDataStore instance for retrieving session data
        ai_interviewer: AIInterviewer instance for LLM-based analysis
        logger: Optional LoggingManager instance
    """

    def __init__(self, data_store, ai_interviewer, logger=None):
        """
        Initialize Evaluation Manager.
        
        Args:
            data_store: IDataStore instance for data retrieval
            ai_interviewer: AIInterviewer instance for analysis
            logger: Optional LoggingManager instance
        """
        self.data_store = data_store
        self.ai_interviewer = ai_interviewer
        self.logger = logger

        if self.logger:
            self.logger.info(
                component="EvaluationManager",
                operation="__init__",
                message="Evaluation Manager initialized",
            )

    def generate_evaluation(self, session_id: str) -> EvaluationReport:
        """
        Generate comprehensive evaluation report for a completed session.
        
        Analyzes conversation history, whiteboard snapshots, and all enabled
        communication modes to produce structured feedback with scores,
        categorized feedback, and improvement plans.
        
        Args:
            session_id: Session identifier
            
        Returns:
            EvaluationReport with complete assessment
            
        Raises:
            AIProviderError: If evaluation generation fails
        """
        if self.logger:
            self.logger.info(
                component="EvaluationManager",
                operation="generate_evaluation",
                message=f"Starting evaluation generation for session {session_id}",
                session_id=session_id,
            )

        try:
            # Retrieve session data
            session = self.data_store.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            conversation_history = self.data_store.get_conversation_history(session_id)
            media_files = self.data_store.get_media_files(session_id)

            # Analyze conversation for competency assessment
            competency_scores = self._analyze_competencies(
                session_id, conversation_history
            )

            # Calculate overall score
            overall_score = self._calculate_overall_score(competency_scores)

            # Generate categorized feedback
            feedback_categories = self._generate_feedback(
                session_id, conversation_history, competency_scores
            )

            # Analyze communication modes
            communication_analysis = self._analyze_communication_modes(
                session_id, session.config.enabled_modes, media_files
            )

            # Generate improvement plan
            improvement_plan = self._generate_improvement_plan(
                session_id, competency_scores, feedback_categories["needs_improvement"]
            )

            # Create evaluation report
            evaluation = EvaluationReport(
                session_id=session_id,
                overall_score=overall_score,
                competency_scores=competency_scores,
                went_well=feedback_categories["went_well"],
                went_okay=feedback_categories["went_okay"],
                needs_improvement=feedback_categories["needs_improvement"],
                improvement_plan=improvement_plan,
                communication_mode_analysis=communication_analysis,
                created_at=datetime.now(),
            )

            # Save evaluation to database
            self.data_store.save_evaluation(evaluation)

            if self.logger:
                self.logger.info(
                    component="EvaluationManager",
                    operation="generate_evaluation",
                    message=f"Evaluation generated successfully for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "overall_score": overall_score,
                        "competency_count": len(competency_scores),
                    },
                )

            return evaluation

        except Exception as e:
            error_msg = f"Failed to generate evaluation for session {session_id}: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="EvaluationManager",
                    operation="generate_evaluation",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e,
                )
            raise AIProviderError(error_msg) from e

    def _analyze_competencies(
        self, session_id: str, conversation_history: List[Message]
    ) -> Dict[str, CompetencyScore]:
        """
        Analyze conversation history to assess key competencies.
        
        Args:
            session_id: Session identifier
            conversation_history: List of conversation messages
            
        Returns:
            Dictionary mapping competency names to scores
        """
        if self.logger:
            self.logger.info(
                component="EvaluationManager",
                operation="analyze_competencies",
                message=f"Analyzing competencies for session {session_id}",
                session_id=session_id,
            )

        # Build conversation context for analysis
        conversation_text = self._format_conversation(conversation_history)

        # Define competencies to evaluate
        competencies = [
            "Problem Decomposition",
            "Scalability Considerations",
            "Reliability & Fault Tolerance",
            "Data Modeling",
            "Trade-off Analysis",
            "Communication Clarity",
            "System Design Patterns",
        ]

        prompt = f"""Analyze the following system design interview conversation and evaluate the candidate's performance across these competencies:

{', '.join(competencies)}

For each competency, provide:
1. A score from 0-100
2. A confidence level (high, medium, low)
3. Specific evidence from the conversation

Conversation:
{conversation_text}

Respond in the following JSON format:
{{
    "Problem Decomposition": {{
        "score": 85,
        "confidence_level": "high",
        "evidence": ["Broke down the URL shortener into clear components", "Identified key services"]
    }},
    ...
}}

Be objective and base scores on actual evidence from the conversation."""

        messages = [
            SystemMessage(
                content="You are an expert technical interviewer evaluating system design interview performance."
            ),
            HumanMessage(content=prompt),
        ]

        # Call LLM for analysis
        response_content, token_usage = self.ai_interviewer._call_llm_with_retry(
            messages, operation="analyze_competencies"
        )

        # Parse response and create CompetencyScore objects
        competency_scores = self._parse_competency_scores(response_content, competencies)

        if self.logger:
            self.logger.info(
                component="EvaluationManager",
                operation="analyze_competencies",
                message=f"Competency analysis completed for session {session_id}",
                session_id=session_id,
                metadata={"competency_count": len(competency_scores)},
            )

        return competency_scores

    def _format_conversation(self, conversation_history: List[Message]) -> str:
        """
        Format conversation history for analysis.
        
        Args:
            conversation_history: List of messages
            
        Returns:
            Formatted conversation string
        """
        formatted = []
        for msg in conversation_history:
            role = "Interviewer" if msg.role == "interviewer" else "Candidate"
            formatted.append(f"{role}: {msg.content}")
        return "\n\n".join(formatted)

    def _parse_competency_scores(
        self, response_content: str, competencies: List[str]
    ) -> Dict[str, CompetencyScore]:
        """
        Parse LLM response to extract competency scores.
        
        Args:
            response_content: LLM response content
            competencies: List of competency names
            
        Returns:
            Dictionary of competency scores
        """
        import json
        import re

        # Try to extract JSON from response
        try:
            # Look for JSON block in response
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response_content)

            competency_scores = {}
            for competency in competencies:
                if competency in data:
                    comp_data = data[competency]
                    competency_scores[competency] = CompetencyScore(
                        score=float(comp_data.get("score", 50)),
                        confidence_level=comp_data.get("confidence_level", "medium"),
                        evidence=comp_data.get("evidence", []),
                    )
                else:
                    # Default score if not found
                    competency_scores[competency] = CompetencyScore(
                        score=50.0,
                        confidence_level="low",
                        evidence=["Insufficient data for assessment"],
                    )

            return competency_scores

        except Exception as e:
            if self.logger:
                self.logger.warning(
                    component="EvaluationManager",
                    operation="parse_competency_scores",
                    message=f"Failed to parse competency scores: {str(e)}",
                    metadata={"response_preview": response_content[:200]},
                )

            # Return default scores
            return {
                competency: CompetencyScore(
                    score=50.0,
                    confidence_level="low",
                    evidence=["Unable to parse evaluation"],
                )
                for competency in competencies
            }

    def _calculate_overall_score(
        self, competency_scores: Dict[str, CompetencyScore]
    ) -> float:
        """
        Calculate overall score from competency scores.
        
        Args:
            competency_scores: Dictionary of competency scores
            
        Returns:
            Overall score (0-100)
        """
        if not competency_scores:
            return 0.0

        total = sum(score.score for score in competency_scores.values())
        return round(total / len(competency_scores), 2)

    def _generate_feedback(
        self,
        session_id: str,
        conversation_history: List[Message],
        competency_scores: Dict[str, CompetencyScore],
    ) -> Dict[str, List[Feedback]]:
        """
        Generate categorized feedback (went_well, went_okay, needs_improvement).
        
        Args:
            session_id: Session identifier
            conversation_history: List of conversation messages
            competency_scores: Competency scores
            
        Returns:
            Dictionary with categorized feedback lists
        """
        if self.logger:
            self.logger.info(
                component="EvaluationManager",
                operation="generate_feedback",
                message=f"Generating feedback for session {session_id}",
                session_id=session_id,
            )

        conversation_text = self._format_conversation(conversation_history)

        # Build competency summary
        competency_summary = "\n".join(
            [
                f"- {name}: {score.score}/100 ({score.confidence_level} confidence)"
                for name, score in competency_scores.items()
            ]
        )

        prompt = f"""Based on the following system design interview conversation and competency scores, provide categorized feedback:

Competency Scores:
{competency_summary}

Conversation:
{conversation_text}

Provide feedback in three categories:
1. **Went Well**: Things the candidate did well (3-5 items)
2. **Went Okay**: Things that were acceptable but could be improved (2-4 items)
3. **Needs Improvement**: Things that need significant improvement (2-4 items)

For each feedback item, provide:
- A clear description
- Specific examples from the conversation

Respond in JSON format:
{{
    "went_well": [
        {{"description": "...", "evidence": ["example 1", "example 2"]}}
    ],
    "went_okay": [
        {{"description": "...", "evidence": ["example 1"]}}
    ],
    "needs_improvement": [
        {{"description": "...", "evidence": ["example 1", "example 2"]}}
    ]
}}"""

        messages = [
            SystemMessage(
                content="You are an expert technical interviewer providing constructive feedback."
            ),
            HumanMessage(content=prompt),
        ]

        response_content, token_usage = self.ai_interviewer._call_llm_with_retry(
            messages, operation="generate_feedback"
        )

        # Parse feedback
        feedback_categories = self._parse_feedback(response_content)

        if self.logger:
            self.logger.info(
                component="EvaluationManager",
                operation="generate_feedback",
                message=f"Feedback generated for session {session_id}",
                session_id=session_id,
                metadata={
                    "went_well_count": len(feedback_categories["went_well"]),
                    "went_okay_count": len(feedback_categories["went_okay"]),
                    "needs_improvement_count": len(feedback_categories["needs_improvement"]),
                },
            )

        return feedback_categories

    def _parse_feedback(self, response_content: str) -> Dict[str, List[Feedback]]:
        """
        Parse LLM response to extract categorized feedback.
        
        Args:
            response_content: LLM response content
            
        Returns:
            Dictionary with feedback categories
        """
        import json
        import re

        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response_content)

            feedback_categories = {
                "went_well": [],
                "went_okay": [],
                "needs_improvement": [],
            }

            for category in feedback_categories.keys():
                if category in data:
                    for item in data[category]:
                        feedback_categories[category].append(
                            Feedback(
                                category=category,
                                description=item.get("description", ""),
                                evidence=item.get("evidence", []),
                            )
                        )

            return feedback_categories

        except Exception as e:
            if self.logger:
                self.logger.warning(
                    component="EvaluationManager",
                    operation="parse_feedback",
                    message=f"Failed to parse feedback: {str(e)}",
                )

            # Return default feedback
            return {
                "went_well": [
                    Feedback(
                        category="went_well",
                        description="Participated in the interview",
                        evidence=[],
                    )
                ],
                "went_okay": [],
                "needs_improvement": [
                    Feedback(
                        category="needs_improvement",
                        description="Unable to generate detailed feedback",
                        evidence=[],
                    )
                ],
            }

    def _analyze_communication_modes(
        self,
        session_id: str,
        enabled_modes: List[CommunicationMode],
        media_files: List[MediaFile],
    ) -> ModeAnalysis:
        """
        Analyze communication mode usage and effectiveness.
        
        Args:
            session_id: Session identifier
            enabled_modes: List of enabled communication modes
            media_files: List of media files from session
            
        Returns:
            ModeAnalysis with assessments for each mode
        """
        if self.logger:
            self.logger.info(
                component="EvaluationManager",
                operation="analyze_communication_modes",
                message=f"Analyzing communication modes for session {session_id}",
                session_id=session_id,
                metadata={"enabled_modes": [mode.value for mode in enabled_modes]},
            )

        analysis = ModeAnalysis()

        # Count media files by type
        media_counts = {}
        for media in media_files:
            media_counts[media.file_type] = media_counts.get(media.file_type, 0) + 1

        # Analyze audio
        if CommunicationMode.AUDIO in enabled_modes:
            audio_count = media_counts.get("audio", 0)
            if audio_count > 0:
                analysis.audio_quality = f"Good - {audio_count} audio recordings captured"
            else:
                analysis.audio_quality = "No audio recordings found"

        # Analyze video
        if CommunicationMode.VIDEO in enabled_modes:
            video_count = media_counts.get("video", 0)
            if video_count > 0:
                analysis.video_presence = f"Present - {video_count} video recordings"
            else:
                analysis.video_presence = "Video enabled but no recordings found"

        # Analyze whiteboard
        if CommunicationMode.WHITEBOARD in enabled_modes:
            whiteboard_count = media_counts.get("whiteboard", 0)
            if whiteboard_count > 5:
                analysis.whiteboard_usage = f"Excellent - {whiteboard_count} snapshots showing active diagram work"
            elif whiteboard_count > 0:
                analysis.whiteboard_usage = f"Good - {whiteboard_count} snapshots captured"
            else:
                analysis.whiteboard_usage = "Whiteboard enabled but no snapshots saved"

        # Analyze screen share
        if CommunicationMode.SCREEN_SHARE in enabled_modes:
            screen_count = media_counts.get("screen", 0)
            if screen_count > 0:
                analysis.screen_share_usage = f"Used - {screen_count} screen captures"
            else:
                analysis.screen_share_usage = "Screen share enabled but not used"

        # Overall communication assessment
        total_media = sum(media_counts.values())
        if total_media > 10:
            analysis.overall_communication = "Excellent use of multiple communication modes"
        elif total_media > 5:
            analysis.overall_communication = "Good use of communication modes"
        elif total_media > 0:
            analysis.overall_communication = "Basic use of communication modes"
        else:
            analysis.overall_communication = "Limited use of communication modes"

        if self.logger:
            self.logger.info(
                component="EvaluationManager",
                operation="analyze_communication_modes",
                message=f"Communication mode analysis completed for session {session_id}",
                session_id=session_id,
                metadata={"total_media_files": total_media},
            )

        return analysis

    def _generate_improvement_plan(
        self,
        session_id: str,
        competency_scores: Dict[str, CompetencyScore],
        needs_improvement: List[Feedback],
    ) -> ImprovementPlan:
        """
        Generate structured improvement plan with actionable steps.
        
        Args:
            session_id: Session identifier
            competency_scores: Competency scores
            needs_improvement: List of areas needing improvement
            
        Returns:
            ImprovementPlan with concrete steps and resources
        """
        if self.logger:
            self.logger.info(
                component="EvaluationManager",
                operation="generate_improvement_plan",
                message=f"Generating improvement plan for session {session_id}",
                session_id=session_id,
            )

        # Identify priority areas (lowest scoring competencies)
        sorted_competencies = sorted(
            competency_scores.items(), key=lambda x: x[1].score
        )
        priority_areas = [name for name, score in sorted_competencies[:3]]

        # Build context for improvement plan
        improvement_context = "\n".join(
            [f"- {item.description}" for item in needs_improvement]
        )

        competency_context = "\n".join(
            [
                f"- {name}: {score.score}/100"
                for name, score in sorted_competencies[:3]
            ]
        )

        prompt = f"""Based on the following areas needing improvement, create a structured improvement plan with concrete, actionable steps:

Priority Competencies (lowest scores):
{competency_context}

Areas Needing Improvement:
{improvement_context}

Create an improvement plan with:
1. 3-5 concrete action items (numbered steps)
2. Specific resources for each step (books, courses, practice sites)
3. Focus on practical, actionable advice

Respond in JSON format:
{{
    "concrete_steps": [
        {{
            "step_number": 1,
            "description": "Practice breaking down complex systems into components",
            "resources": ["System Design Primer on GitHub", "Designing Data-Intensive Applications book"]
        }}
    ],
    "resources": ["General resource 1", "General resource 2"]
}}"""

        messages = [
            SystemMessage(
                content="You are an expert technical interviewer creating improvement plans."
            ),
            HumanMessage(content=prompt),
        ]

        response_content, token_usage = self.ai_interviewer._call_llm_with_retry(
            messages, operation="generate_improvement_plan"
        )

        # Parse improvement plan
        improvement_plan = self._parse_improvement_plan(
            response_content, priority_areas
        )

        if self.logger:
            self.logger.info(
                component="EvaluationManager",
                operation="generate_improvement_plan",
                message=f"Improvement plan generated for session {session_id}",
                session_id=session_id,
                metadata={"step_count": len(improvement_plan.concrete_steps)},
            )

        return improvement_plan

    def _parse_improvement_plan(
        self, response_content: str, priority_areas: List[str]
    ) -> ImprovementPlan:
        """
        Parse LLM response to extract improvement plan.
        
        Args:
            response_content: LLM response content
            priority_areas: List of priority improvement areas
            
        Returns:
            ImprovementPlan object
        """
        import json
        import re

        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response_content)

            concrete_steps = []
            if "concrete_steps" in data:
                for step_data in data["concrete_steps"]:
                    concrete_steps.append(
                        ActionItem(
                            step_number=step_data.get("step_number", len(concrete_steps) + 1),
                            description=step_data.get("description", ""),
                            resources=step_data.get("resources", []),
                        )
                    )

            return ImprovementPlan(
                priority_areas=priority_areas,
                concrete_steps=concrete_steps,
                resources=data.get("resources", []),
            )

        except Exception as e:
            if self.logger:
                self.logger.warning(
                    component="EvaluationManager",
                    operation="parse_improvement_plan",
                    message=f"Failed to parse improvement plan: {str(e)}",
                )

            # Return default improvement plan
            return ImprovementPlan(
                priority_areas=priority_areas,
                concrete_steps=[
                    ActionItem(
                        step_number=1,
                        description="Review system design fundamentals",
                        resources=["System Design Primer", "Designing Data-Intensive Applications"],
                    ),
                    ActionItem(
                        step_number=2,
                        description="Practice with mock interviews",
                        resources=["Pramp", "interviewing.io"],
                    ),
                ],
                resources=["System Design Interview book by Alex Xu"],
            )
