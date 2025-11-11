"""
Token tracking system for AI API usage monitoring and cost estimation.

This module provides the TokenTracker class for recording, aggregating, and
analyzing token usage across interview sessions with provider-specific pricing.
"""

from datetime import datetime
from typing import Dict, Optional

from src.models import TokenUsage, SessionTokenUsage
from src.database.data_store import IDataStore


# Provider pricing per 1M tokens (as of 2024)
# Prices are in USD per 1 million tokens
PROVIDER_PRICING = {
    "openai": {
        "gpt-4-turbo-preview": {
            "input": 10.00,  # $10 per 1M input tokens
            "output": 30.00,  # $30 per 1M output tokens
        },
        "gpt-4": {
            "input": 30.00,
            "output": 60.00,
        },
        "gpt-3.5-turbo": {
            "input": 0.50,
            "output": 1.50,
        },
    },
    "anthropic": {
        "claude-3-opus-20240229": {
            "input": 15.00,  # $15 per 1M input tokens
            "output": 75.00,  # $75 per 1M output tokens
        },
        "claude-3-sonnet-20240229": {
            "input": 3.00,
            "output": 15.00,
        },
        "claude-3-haiku-20240307": {
            "input": 0.25,
            "output": 1.25,
        },
    },
}


class TokenTracker:
    """
    Token usage tracker for AI API calls.
    
    Tracks token consumption, calculates costs, and provides usage analytics
    for interview sessions. Supports multiple AI providers with different
    pricing models.
    
    Attributes:
        data_store: Data store interface for persisting token usage
        logger: Optional logging manager for tracking operations
    """

    def __init__(self, data_store: IDataStore, logger=None):
        """
        Initialize TokenTracker with data store.
        
        Args:
            data_store: IDataStore implementation for persistence
            logger: Optional LoggingManager instance
        """
        self.data_store = data_store
        self.logger = logger

    def record_usage(
        self,
        session_id: str,
        provider: str,
        model: str,
        operation: str,
        input_tokens: int,
        output_tokens: int,
    ) -> TokenUsage:
        """
        Record token usage for an AI API call.
        
        Calculates total tokens and estimated cost based on provider pricing,
        then persists the record to the database.
        
        Args:
            session_id: Session identifier
            provider: AI provider name (e.g., 'openai', 'anthropic')
            model: Model name (e.g., 'gpt-4-turbo-preview')
            operation: Operation type (e.g., 'question_generation', 'response_analysis')
            input_tokens: Number of input tokens consumed
            output_tokens: Number of output tokens generated
            
        Returns:
            TokenUsage object with calculated cost
            
        Raises:
            ValueError: If provider or model is not recognized
        """
        if self.logger:
            self.logger.debug(
                component="TokenTracker",
                operation="record_usage",
                message=f"Recording token usage for session {session_id}",
                session_id=session_id,
                metadata={
                    "provider": provider,
                    "model": model,
                    "operation": operation,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                },
            )

        # Calculate total tokens
        total_tokens = input_tokens + output_tokens

        # Calculate estimated cost
        estimated_cost = self._calculate_cost(
            provider, model, input_tokens, output_tokens
        )

        # Create TokenUsage object
        token_usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            provider=provider,
            model=model,
            operation=operation,
        )

        # Persist to database
        try:
            self.data_store.save_token_usage(session_id, token_usage)
            if self.logger:
                self.logger.info(
                    component="TokenTracker",
                    operation="record_usage",
                    message=f"Token usage recorded for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "total_tokens": total_tokens,
                        "estimated_cost": estimated_cost,
                        "operation": operation,
                    },
                )
        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="TokenTracker",
                    operation="record_usage",
                    message=f"Failed to save token usage for session {session_id}",
                    session_id=session_id,
                    exc_info=e,
                )
            raise

        return token_usage

    def get_session_usage(self, session_id: str) -> SessionTokenUsage:
        """
        Get aggregated token usage summary for a session.
        
        Retrieves all token usage records for the session and aggregates them
        into a summary with total tokens, total cost, and breakdown by operation.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionTokenUsage with aggregated statistics
        """
        if self.logger:
            self.logger.debug(
                component="TokenTracker",
                operation="get_session_usage",
                message=f"Retrieving token usage for session {session_id}",
                session_id=session_id,
            )

        # Retrieve all token usage records for the session
        usage_records = self.data_store.get_token_usage(session_id)

        # Initialize aggregation variables
        total_input_tokens = 0
        total_output_tokens = 0
        total_tokens = 0
        total_cost = 0.0
        breakdown_by_operation: Dict[str, TokenUsage] = {}

        # Aggregate token usage
        for record in usage_records:
            total_input_tokens += record.input_tokens
            total_output_tokens += record.output_tokens
            total_tokens += record.total_tokens
            total_cost += record.estimated_cost

            # Aggregate by operation type
            operation = record.operation
            if operation in breakdown_by_operation:
                existing = breakdown_by_operation[operation]
                breakdown_by_operation[operation] = TokenUsage(
                    input_tokens=existing.input_tokens + record.input_tokens,
                    output_tokens=existing.output_tokens + record.output_tokens,
                    total_tokens=existing.total_tokens + record.total_tokens,
                    estimated_cost=existing.estimated_cost + record.estimated_cost,
                    provider=record.provider,
                    model=record.model,
                    operation=operation,
                )
            else:
                breakdown_by_operation[operation] = record

        session_usage = SessionTokenUsage(
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_tokens=total_tokens,
            total_cost=total_cost,
            breakdown_by_operation=breakdown_by_operation,
        )

        if self.logger:
            self.logger.info(
                component="TokenTracker",
                operation="get_session_usage",
                message=f"Retrieved token usage for session {session_id}",
                session_id=session_id,
                metadata={
                    "total_tokens": total_tokens,
                    "total_cost": total_cost,
                    "num_operations": len(breakdown_by_operation),
                },
            )

        return session_usage

    def get_total_cost(self, session_id: str) -> float:
        """
        Get total estimated cost for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Total estimated cost in USD
        """
        session_usage = self.get_session_usage(session_id)
        return session_usage.total_cost

    def get_usage_breakdown(self, session_id: str) -> Dict[str, TokenUsage]:
        """
        Get token usage breakdown by operation type.
        
        Returns a dictionary mapping operation types to their aggregated
        token usage statistics.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary mapping operation names to TokenUsage objects
        """
        session_usage = self.get_session_usage(session_id)
        return session_usage.breakdown_by_operation

    def _calculate_cost(
        self, provider: str, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """
        Calculate estimated cost based on provider pricing.
        
        Args:
            provider: AI provider name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
            
        Raises:
            ValueError: If provider or model is not recognized
        """
        # Normalize provider name
        provider_lower = provider.lower()

        # Check if provider exists
        if provider_lower not in PROVIDER_PRICING:
            if self.logger:
                self.logger.warning(
                    component="TokenTracker",
                    operation="_calculate_cost",
                    message=f"Unknown provider '{provider}', using default pricing",
                    metadata={"provider": provider, "model": model},
                )
            # Use default pricing if provider not found
            input_cost_per_million = 10.00
            output_cost_per_million = 30.00
        else:
            # Check if model exists for provider
            if model not in PROVIDER_PRICING[provider_lower]:
                if self.logger:
                    self.logger.warning(
                        component="TokenTracker",
                        operation="_calculate_cost",
                        message=f"Unknown model '{model}' for provider '{provider}', using default pricing",
                        metadata={"provider": provider, "model": model},
                    )
                # Use default pricing for provider if model not found
                # Get first model's pricing as default
                first_model = next(iter(PROVIDER_PRICING[provider_lower].values()))
                input_cost_per_million = first_model["input"]
                output_cost_per_million = first_model["output"]
            else:
                pricing = PROVIDER_PRICING[provider_lower][model]
                input_cost_per_million = pricing["input"]
                output_cost_per_million = pricing["output"]

        # Calculate cost (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * input_cost_per_million
        output_cost = (output_tokens / 1_000_000) * output_cost_per_million
        total_cost = input_cost + output_cost

        return round(total_cost, 6)  # Round to 6 decimal places for precision
