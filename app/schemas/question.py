"""Pydantic validation schemas for Practice Questions and Attempts.

Adheres strictly to docs/05_QUESTIONS_PRACTICE_PROGRESS.md:
- Stem
- Exactly 4 options (A, B, C, D)
- Valid correct_option present in options
- Rationale for correct answer and distractors
- Domain / Task mapping
- Verification status and origin metadata
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class QuestionOption(BaseModel):
    id: str = Field(..., description="Option letter: A, B, C, or D")
    text: str = Field(..., min_length=1, description="Option answer text")


class QuestionSchema(BaseModel):
    """Validated schema for a 4-choice multiple-choice item."""

    stem: str = Field(..., min_length=10, description="The clinical or behavioral scenario / question stem")
    options: List[QuestionOption] = Field(..., min_length=4, max_length=4, description="Exactly 4 distinct options")
    correct_option: str = Field(..., description="The key of the correct option: A, B, C, or D")
    rationale: str = Field(..., min_length=10, description="Technical rationale for the correct answer")
    distractor_rationales: Dict[str, str] = Field(
        default_factory=dict,
        description="Rationales explaining why distractors are incorrect",
    )
    task_code: Optional[str] = Field(None, description="e.g. 'B.4' or 'A.1'")
    domain_code: Optional[str] = Field(None, description="e.g. 'A' through 'I'")
    difficulty: str = Field("medium", description="easy, medium, hard")
    origin_type: str = Field("unclassified", description="manual, adapted, generated, or unclassified")
    source: str = Field("PTB ABA Exam Study Manual 6th Edition", description="Source citation or reference")
    verification_status: str = Field("unverified", description="verified, unverified, flagged")

    @field_validator("correct_option")
    @classmethod
    def validate_correct_option_key(cls, v: str) -> str:
        key = v.strip().upper()
        if key not in ("A", "B", "C", "D"):
            raise ValueError(f"correct_option must be one of 'A', 'B', 'C', 'D', got '{v}'")
        return key

    @model_validator(mode="after")
    def validate_options_and_correctness(self) -> QuestionSchema:
        option_ids = [opt.id.strip().upper() for opt in self.options]
        if len(set(option_ids)) != 4:
            raise ValueError("Question options must have 4 unique option IDs (A, B, C, D)")

        if self.correct_option not in option_ids:
            raise ValueError(f"Correct option '{self.correct_option}' is not among option IDs: {option_ids}")

        return self


class AttemptSubmissionSchema(BaseModel):
    """Schema for validating candidate answer submissions."""

    question_id: int
    selected_option: str
    confidence: Optional[str] = Field("medium", description="low, medium, high")
    response_time_seconds: Optional[float] = Field(0.0, ge=0.0)

    @field_validator("selected_option")
    @classmethod
    def validate_selected_option(cls, v: str) -> str:
        key = v.strip().upper()
        if key not in ("A", "B", "C", "D"):
            raise ValueError(f"selected_option must be one of 'A', 'B', 'C', 'D', got '{v}'")
        return key

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: Optional[str]) -> str:
        if not v:
            return "medium"
        c = v.strip().lower()
        if c not in ("low", "medium", "high"):
            return "medium"
        return c
