"""
Resume Manager for parsing and extracting candidate information from resumes.

This module provides the ResumeManager class which handles resume upload,
parsing using LLM, and extraction of structured data including experience level,
domain expertise, work history, and education.
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import PyPDF2

from src.models import ResumeData, WorkExperience, Education
from src.database.data_store import IDataStore
from src.exceptions import ValidationError, AIProviderError
from src.config import Config


class ResumeManager:
    """
    Manages resume upload, parsing, and data extraction.
    
    The ResumeManager uses LLM to extract structured information from resumes
    in PDF or text format, including experience level, domain expertise,
    work history, and education.
    
    Attributes:
        data_store: DataStore instance for persistence
        config: Configuration object
        logger: Optional LoggingManager instance
        llm_client: LLM client for resume parsing (OpenAI or Anthropic)
    """

    def __init__(
        self,
        data_store: IDataStore,
        config: Config,
        logger=None,
    ):
        """
        Initialize ResumeManager with dependencies.
        
        Args:
            data_store: DataStore instance for persistence
            config: Configuration object
            logger: Optional LoggingManager instance
        """
        self.data_store = data_store
        self.config = config
        self.logger = logger
        self.llm_client = None
        self._initialize_llm_client()

    def _initialize_llm_client(self) -> None:
        """Initialize LLM client for resume parsing."""
        # Try OpenAI first, then Anthropic
        if "openai" in self.config.ai_providers and self.config.ai_providers["openai"].api_key:
            try:
                import openai
                self.llm_client = openai.OpenAI(
                    api_key=self.config.ai_providers["openai"].api_key
                )
                self.llm_provider = "openai"
                self.llm_model = self.config.ai_providers["openai"].default_model
                if self.logger:
                    self.logger.info(
                        component="ResumeManager",
                        operation="initialize_llm_client",
                        message="Initialized OpenAI client for resume parsing",
                    )
            except ImportError:
                if self.logger:
                    self.logger.warning(
                        component="ResumeManager",
                        operation="initialize_llm_client",
                        message="OpenAI library not installed",
                    )
        elif "anthropic" in self.config.ai_providers and self.config.ai_providers["anthropic"].api_key:
            try:
                import anthropic
                self.llm_client = anthropic.Anthropic(
                    api_key=self.config.ai_providers["anthropic"].api_key
                )
                self.llm_provider = "anthropic"
                self.llm_model = self.config.ai_providers["anthropic"].default_model
                if self.logger:
                    self.logger.info(
                        component="ResumeManager",
                        operation="initialize_llm_client",
                        message="Initialized Anthropic client for resume parsing",
                    )
            except ImportError:
                if self.logger:
                    self.logger.warning(
                        component="ResumeManager",
                        operation="initialize_llm_client",
                        message="Anthropic library not installed",
                    )

        if not self.llm_client:
            error_msg = "No LLM client available for resume parsing. Install openai or anthropic library."
            if self.logger:
                self.logger.error(
                    component="ResumeManager",
                    operation="initialize_llm_client",
                    message=error_msg,
                )
            raise AIProviderError(error_msg)

    def upload_resume(self, file_path: str, user_id: str) -> ResumeData:
        """
        Upload and parse a resume file.
        
        Args:
            file_path: Path to the resume file (PDF or TXT)
            user_id: User identifier
            
        Returns:
            ResumeData object with extracted information
            
        Raises:
            ValidationError: If file format is invalid or file doesn't exist
            AIProviderError: If LLM parsing fails
        """
        if self.logger:
            self.logger.info(
                component="ResumeManager",
                operation="upload_resume",
                message=f"Uploading resume for user {user_id}",
                user_id=user_id,
                metadata={"file_path": file_path},
            )

        # Validate file exists
        if not os.path.exists(file_path):
            raise ValidationError(f"Resume file not found: {file_path}")

        # Validate file format
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in [".pdf", ".txt"]:
            raise ValidationError(
                f"Unsupported file format: {file_ext}. Only PDF and TXT files are supported."
            )

        # Parse resume
        resume_data = self.parse_resume(file_path)
        resume_data.user_id = user_id

        # Save to database
        self.save_resume(user_id, resume_data)

        if self.logger:
            self.logger.info(
                component="ResumeManager",
                operation="upload_resume",
                message=f"Resume uploaded and parsed successfully for user {user_id}",
                user_id=user_id,
                metadata={
                    "experience_level": resume_data.experience_level,
                    "years_of_experience": resume_data.years_of_experience,
                    "domain_count": len(resume_data.domain_expertise),
                },
            )

        return resume_data

    def parse_resume(self, file_path: str) -> ResumeData:
        """
        Parse resume file and extract structured data using LLM.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            ResumeData object with extracted information
            
        Raises:
            ValidationError: If file cannot be read
            AIProviderError: If LLM parsing fails
        """
        if self.logger:
            self.logger.info(
                component="ResumeManager",
                operation="parse_resume",
                message=f"Parsing resume file: {file_path}",
            )

        # Extract text from file
        raw_text = self._extract_text_from_file(file_path)

        if not raw_text or len(raw_text.strip()) < 50:
            raise ValidationError("Resume file appears to be empty or too short")

        # Use LLM to extract structured data
        extracted_data = self._extract_data_with_llm(raw_text)

        # Create ResumeData object
        resume_data = ResumeData(
            user_id="",  # Will be set by upload_resume
            name=extracted_data.get("name", ""),
            email=extracted_data.get("email", ""),
            experience_level=extracted_data.get("experience_level", "mid"),
            years_of_experience=extracted_data.get("years_of_experience", 0),
            domain_expertise=extracted_data.get("domain_expertise", []),
            work_experience=[
                WorkExperience(
                    company=exp.get("company", ""),
                    title=exp.get("title", ""),
                    duration=exp.get("duration", ""),
                    description=exp.get("description", ""),
                )
                for exp in extracted_data.get("work_experience", [])
            ],
            education=[
                Education(
                    institution=edu.get("institution", ""),
                    degree=edu.get("degree", ""),
                    field=edu.get("field", ""),
                    year=edu.get("year", ""),
                )
                for edu in extracted_data.get("education", [])
            ],
            skills=extracted_data.get("skills", []),
            raw_text=raw_text,
        )

        if self.logger:
            self.logger.info(
                component="ResumeManager",
                operation="parse_resume",
                message="Resume parsed successfully",
                metadata={
                    "name": resume_data.name,
                    "experience_level": resume_data.experience_level,
                    "years_of_experience": resume_data.years_of_experience,
                },
            )

        return resume_data

    def _extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text content from PDF or TXT file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
            
        Raises:
            ValidationError: If file cannot be read
        """
        file_ext = Path(file_path).suffix.lower()

        try:
            if file_ext == ".pdf":
                return self._extract_text_from_pdf(file_path)
            elif file_ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                raise ValidationError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="ResumeManager",
                    operation="_extract_text_from_file",
                    message=f"Failed to extract text from file: {file_path}",
                    exc_info=e,
                )
            raise ValidationError(f"Failed to read resume file: {str(e)}")

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        text_parts = []
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts)

    def _extract_data_with_llm(self, raw_text: str) -> Dict[str, Any]:
        """
        Extract structured data from resume text using LLM.
        
        Args:
            raw_text: Raw resume text
            
        Returns:
            Dictionary with extracted structured data
            
        Raises:
            AIProviderError: If LLM call fails
        """
        prompt = self._build_extraction_prompt(raw_text)

        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a resume parser that extracts structured information from resumes. Always respond with valid JSON only, no additional text.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content
            elif self.llm_provider == "anthropic":
                response = self.llm_client.messages.create(
                    model=self.llm_model,
                    max_tokens=2000,
                    temperature=0.1,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                )
                content = response.content[0].text
            else:
                raise AIProviderError(f"Unsupported LLM provider: {self.llm_provider}")

            # Parse JSON response
            extracted_data = json.loads(content)

            if self.logger:
                self.logger.info(
                    component="ResumeManager",
                    operation="_extract_data_with_llm",
                    message="Successfully extracted data from resume using LLM",
                    metadata={
                        "provider": self.llm_provider,
                        "model": self.llm_model,
                    },
                )

            return extracted_data

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="ResumeManager",
                    operation="_extract_data_with_llm",
                    message=error_msg,
                    exc_info=e,
                )
            raise AIProviderError(error_msg)
        except Exception as e:
            error_msg = f"LLM resume parsing failed: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="ResumeManager",
                    operation="_extract_data_with_llm",
                    message=error_msg,
                    exc_info=e,
                )
            raise AIProviderError(error_msg)

    def _build_extraction_prompt(self, raw_text: str) -> str:
        """
        Build prompt for LLM to extract structured data from resume.
        
        Args:
            raw_text: Raw resume text
            
        Returns:
            Formatted prompt string
        """
        return f"""Extract structured information from the following resume and return it as JSON.

Resume text:
{raw_text}

Extract the following information and return as JSON with these exact keys:
{{
  "name": "Full name of the candidate",
  "email": "Email address",
  "experience_level": "One of: junior, mid, senior, staff (based on years and role seniority)",
  "years_of_experience": <number of years of professional experience>,
  "domain_expertise": ["list", "of", "domain", "areas", "like", "backend", "distributed-systems", "cloud", "frontend"],
  "work_experience": [
    {{
      "company": "Company name",
      "title": "Job title",
      "duration": "Duration (e.g., '2020-2022' or '2 years')",
      "description": "Brief description of role and responsibilities"
    }}
  ],
  "education": [
    {{
      "institution": "University/School name",
      "degree": "Degree type (e.g., 'Bachelor of Science')",
      "field": "Field of study (e.g., 'Computer Science')",
      "year": "Graduation year or duration"
    }}
  ],
  "skills": ["list", "of", "technical", "skills"]
}}

Guidelines for experience_level:
- "junior": 0-2 years of experience, entry-level roles
- "mid": 3-5 years of experience, intermediate roles
- "senior": 6-10 years of experience, senior roles
- "staff": 10+ years of experience, staff/principal/lead roles

Guidelines for domain_expertise:
- Use lowercase with hyphens (e.g., "distributed-systems", "machine-learning")
- Common domains: backend, frontend, full-stack, distributed-systems, cloud, devops, data-engineering, machine-learning, mobile, security

Return ONLY the JSON object, no additional text or explanation."""

    def extract_experience_level(self, resume_data: ResumeData) -> str:
        """
        Extract experience level from resume data.
        
        Args:
            resume_data: ResumeData object
            
        Returns:
            Experience level (junior, mid, senior, staff)
        """
        return resume_data.experience_level

    def extract_domain_expertise(self, resume_data: ResumeData) -> List[str]:
        """
        Extract domain expertise from resume data.
        
        Args:
            resume_data: ResumeData object
            
        Returns:
            List of domain expertise areas
        """
        return resume_data.domain_expertise

    def get_resume(self, user_id: str) -> Optional[ResumeData]:
        """
        Retrieve resume data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            ResumeData if found, None otherwise
        """
        if self.logger:
            self.logger.debug(
                component="ResumeManager",
                operation="get_resume",
                message=f"Retrieving resume for user {user_id}",
                user_id=user_id,
            )

        resume_data = self.data_store.get_resume(user_id)

        if resume_data and self.logger:
            self.logger.info(
                component="ResumeManager",
                operation="get_resume",
                message=f"Resume found for user {user_id}",
                user_id=user_id,
            )
        elif self.logger:
            self.logger.info(
                component="ResumeManager",
                operation="get_resume",
                message=f"No resume found for user {user_id}",
                user_id=user_id,
            )

        return resume_data

    def save_resume(self, user_id: str, resume_data: ResumeData) -> None:
        """
        Save resume data to database.
        
        Args:
            user_id: User identifier
            resume_data: ResumeData object to save
        """
        if self.logger:
            self.logger.info(
                component="ResumeManager",
                operation="save_resume",
                message=f"Saving resume for user {user_id}",
                user_id=user_id,
                metadata={
                    "experience_level": resume_data.experience_level,
                    "years_of_experience": resume_data.years_of_experience,
                },
            )

        # Ensure user_id is set
        resume_data.user_id = user_id

        try:
            self.data_store.save_resume(resume_data)

            if self.logger:
                self.logger.info(
                    component="ResumeManager",
                    operation="save_resume",
                    message=f"Resume saved successfully for user {user_id}",
                    user_id=user_id,
                )
        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="ResumeManager",
                    operation="save_resume",
                    message=f"Failed to save resume for user {user_id}",
                    user_id=user_id,
                    exc_info=e,
                )
            raise
