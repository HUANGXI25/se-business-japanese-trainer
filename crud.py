from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from models import MistakeNote, PracticeSession, PracticeTurn, Setting


def utc_now_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def get_or_create_settings(db: Session) -> Setting:
    settings = db.get(Setting, 1)
    if settings:
        return settings

    settings = Setting(id=1)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def update_settings(db: Session, payload: dict) -> Setting:
    settings = get_or_create_settings(db)
    for key, value in payload.items():
        setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings


def create_session(db: Session, scenario: dict, mode: str, start_turn: int = 1) -> PracticeSession:
    scenario_turns = scenario.get("turns", [])
    safe_start_turn = min(max(1, start_turn), len(scenario_turns))
    session = PracticeSession(
        scenario_id=scenario["id"],
        scenario_title=scenario["title"],
        difficulty=scenario["difficulty"],
        category=scenario["category"],
        mode=mode,
        start_turn=safe_start_turn,
        total_turns=max(1, len(scenario_turns) - safe_start_turn + 1),
        completed_turns=0,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: int) -> PracticeSession | None:
    return db.get(PracticeSession, session_id)


def get_mistake_note(db: Session, mistake_id: int) -> MistakeNote | None:
    return db.get(MistakeNote, mistake_id)


def get_next_attempt_index(db: Session, session_id: int, turn_number: int) -> int:
    count = db.scalar(
        select(func.count(PracticeTurn.id)).where(
            PracticeTurn.session_id == session_id,
            PracticeTurn.turn_number == turn_number,
        )
    )
    return int(count or 0) + 1


def create_turn_attempt(
    db: Session,
    session: PracticeSession,
    turn_number: int,
    prompt: str,
    response: str,
    score_result,
    correction: dict,
    recommendation: dict,
    passed: bool,
) -> PracticeTurn:
    attempt = PracticeTurn(
        session_id=session.id,
        scenario_id=session.scenario_id,
        turn_number=turn_number,
        attempt_index=get_next_attempt_index(db, session.id, turn_number),
        mode=session.mode,
        prompt=prompt,
        user_response=response,
        total_score=score_result.total_score,
        keigo_score=score_result.scores["敬语准确度"],
        business_score=score_result.scores["商务自然度"],
        scenario_fit_score=score_result.scores["场景适配度"],
        logic_score=score_result.scores["表达逻辑"],
        completeness_score=score_result.scores["回答完整度"],
        passed=passed,
        summary=score_result.summary,
        detailed_feedback=score_result.detailed_feedback,
        correction_json=json.dumps(correction, ensure_ascii=False),
        recommendation_json=json.dumps(recommendation, ensure_ascii=False),
        issue_tags=json.dumps(score_result.issue_tags, ensure_ascii=False),
        low_dimensions=json.dumps(score_result.low_dimensions, ensure_ascii=False),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def advance_session(db: Session, session: PracticeSession, turn_score: int) -> PracticeSession:
    session.completed_turns += 1
    session.total_score += turn_score
    session.average_score = round(session.total_score / max(1, session.completed_turns))
    if session.completed_turns >= session.total_turns:
        session.is_completed = True
        session.completed_at = utc_now_naive()
    db.commit()
    db.refresh(session)
    return session


def save_mistake_note(
    db: Session,
    session: PracticeSession,
    practice_turn_id: int | None,
    turn_number: int,
    response: str,
    low_dimensions: list[str],
    issue_tags: list[str],
    recommended_expression: str,
) -> MistakeNote:
    note = MistakeNote(
        session_id=session.id,
        practice_turn_id=practice_turn_id,
        scenario_title=session.scenario_title,
        turn_number=turn_number,
        user_response=response,
        low_dimensions=",".join(low_dimensions),
        issue_tags=",".join(issue_tags),
        recommended_expression=recommended_expression,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def list_sessions(db: Session) -> list[PracticeSession]:
    return list(
        db.scalars(select(PracticeSession).order_by(desc(PracticeSession.started_at)))
    )


def list_session_turns(db: Session, session_id: int) -> list[PracticeTurn]:
    return list(
        db.scalars(
            select(PracticeTurn)
            .where(PracticeTurn.session_id == session_id)
            .order_by(PracticeTurn.turn_number, PracticeTurn.attempt_index)
        )
    )


def list_all_turns(db: Session) -> list[PracticeTurn]:
    return list(
        db.scalars(select(PracticeTurn).order_by(desc(PracticeTurn.created_at)))
    )


def list_mistake_notes(db: Session) -> list[MistakeNote]:
    return list(
        db.scalars(select(MistakeNote).order_by(desc(MistakeNote.created_at)))
    )
