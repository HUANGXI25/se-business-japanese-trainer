from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def utc_now_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scenario_id: Mapped[str] = mapped_column(String(50), index=True)
    scenario_title: Mapped[str] = mapped_column(String(255))
    difficulty: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(50))
    mode: Mapped[str] = mapped_column(String(20), index=True)
    start_turn: Mapped[int] = mapped_column(Integer, default=1)
    total_turns: Mapped[int] = mapped_column(Integer, default=0)
    completed_turns: Mapped[int] = mapped_column(Integer, default=0)
    total_score: Mapped[int] = mapped_column(Integer, default=0)
    average_score: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    turns: Mapped[list["PracticeTurn"]] = relationship(
        "PracticeTurn",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    mistake_notes: Mapped[list["MistakeNote"]] = relationship(
        "MistakeNote",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class PracticeTurn(Base):
    __tablename__ = "practice_turns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("practice_sessions.id"), index=True)
    scenario_id: Mapped[str] = mapped_column(String(50), index=True)
    turn_number: Mapped[int] = mapped_column(Integer)
    attempt_index: Mapped[int] = mapped_column(Integer, default=1)
    mode: Mapped[str] = mapped_column(String(20))
    prompt: Mapped[str] = mapped_column(Text)
    user_response: Mapped[str] = mapped_column(Text)
    total_score: Mapped[int] = mapped_column(Integer)
    keigo_score: Mapped[int] = mapped_column(Integer)
    business_score: Mapped[int] = mapped_column(Integer)
    scenario_fit_score: Mapped[int] = mapped_column(Integer)
    logic_score: Mapped[int] = mapped_column(Integer)
    completeness_score: Mapped[int] = mapped_column(Integer)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    summary: Mapped[str] = mapped_column(Text)
    detailed_feedback: Mapped[str] = mapped_column(Text)
    correction_json: Mapped[str] = mapped_column(Text)
    recommendation_json: Mapped[str] = mapped_column(Text)
    issue_tags: Mapped[str] = mapped_column(Text)
    low_dimensions: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)

    session: Mapped["PracticeSession"] = relationship("PracticeSession", back_populates="turns")


class MistakeNote(Base):
    __tablename__ = "mistake_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("practice_sessions.id"), index=True)
    practice_turn_id: Mapped[int | None] = mapped_column(
        ForeignKey("practice_turns.id"),
        nullable=True,
    )
    scenario_title: Mapped[str] = mapped_column(String(255))
    turn_number: Mapped[int] = mapped_column(Integer)
    user_response: Mapped[str] = mapped_column(Text)
    low_dimensions: Mapped[str] = mapped_column(Text)
    issue_tags: Mapped[str] = mapped_column(Text)
    recommended_expression: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)

    session: Mapped["PracticeSession"] = relationship("PracticeSession", back_populates="mistake_notes")


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    default_mode: Mapped[str] = mapped_column(String(20), default="learning")
    difficulty_filter: Mapped[str] = mapped_column(String(20), default="all")
    show_hints: Mapped[bool] = mapped_column(Boolean, default=True)
    save_low_scores: Mapped[bool] = mapped_column(Boolean, default=True)
    low_score_threshold: Mapped[int] = mapped_column(Integer, default=32)
