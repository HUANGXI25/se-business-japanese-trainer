from typing import Any

from pydantic import BaseModel, Field


class ResponseSubmission(BaseModel):
    response_text: str = Field(..., min_length=1)


class SettingsUpdate(BaseModel):
    default_mode: str
    difficulty_filter: str
    show_hints: bool
    save_low_scores: bool
    low_score_threshold: int = Field(default=32, ge=10, le=50)


class TurnState(BaseModel):
    session_id: int
    scenario_id: str
    scenario_title: str
    description: str
    difficulty: str
    category: str
    mode: str
    turn_number: int | None
    total_turns: int
    speaker_line: str | None
    task_label: str | None
    task_breakdown: list[str] = []
    keywords: list[str] = []
    sentence_frames: list[str] = []
    reference_answers: list[str] = []
    recommended_phrases: list[str] = []
    progress_text: str
    show_hints: bool
    can_view_reference: bool = False
    completed: bool = False
    completion_summary: dict[str, Any] | None = None


class TurnFeedback(BaseModel):
    passed: bool
    completed: bool
    can_continue: bool
    mode: str
    total_score: int
    scores: dict[str, int]
    dimension_feedback: dict[str, str]
    fragment_issues: list[dict[str, str]]
    summary: str
    detailed_feedback: str
    correction: dict[str, Any]
    recommendation: dict[str, Any]
    reference_answers: list[str] = []
    issue_tags: list[str]
    low_dimensions: list[str]
    next_turn_available: bool
    completion_summary: dict[str, Any] | None = None
