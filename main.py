from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import crud
from analytics_engine import build_weakness_analysis
from database import get_db, init_db
from llm_interface import evaluate_response, generate_feedback
from scenario_loader import (
    get_categories,
    get_scenario,
    get_scenario_by_title,
    get_turn,
    list_scenarios,
    load_scenarios,
)
from schemas import ResponseSubmission

init_db()
load_scenarios()

app = FastAPI(title="Business Japanese SE Roleplay Trainer")
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

MODE_LABELS = {
    "learning": "学习模式",
    "practice": "实战模式",
}

DIFFICULTY_LABELS = {
    "easy": "初级",
    "medium": "中级",
    "hard": "高级",
    "all": "全部",
}

CATEGORY_LABELS = {
    "reporting": "汇报沟通",
    "requirement_confirmation": "需求确认",
    "meeting": "会议发言",
    "client_communication": "客户沟通",
    "incident": "问题汇报",
    "coordination": "优先级协调",
    "collaboration": "协作求助",
    "apology": "致歉说明",
    "schedule": "日程协调",
    "clarification": "礼貌追问",
    "escalation": "升级汇报",
    "risk_management": "风险管理",
    "testing": "测试反馈",
    "team_communication": "团队共享",
    "review": "代码审阅",
    "release": "发布确认",
    "attendance": "出勤说明",
    "all": "全部",
}


def _page_context(request: Request, db: Session) -> dict:
    settings = crud.get_or_create_settings(db)
    return {
        "request": request,
        "settings": settings,
        "mode_labels": MODE_LABELS,
        "difficulty_labels": DIFFICULTY_LABELS,
        "category_labels": CATEGORY_LABELS,
    }


def _build_turn_state(db: Session, session_id: int) -> dict:
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    scenario = get_scenario(session.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    settings = crud.get_or_create_settings(db)
    show_hints = session.mode == "learning" and settings.show_hints

    if session.is_completed:
        return {
            "session_id": session.id,
            "scenario_id": session.scenario_id,
            "scenario_title": session.scenario_title,
            "description": scenario["description"],
            "difficulty": session.difficulty,
            "category": session.category,
            "mode": session.mode,
            "turn_number": None,
            "total_turns": session.total_turns,
            "speaker_line": None,
            "task_label": None,
            "task_breakdown": [],
            "keywords": [],
            "sentence_frames": [],
            "reference_answers": [],
            "recommended_phrases": [],
            "progress_text": f"已完成 {session.total_turns}/{session.total_turns}",
            "show_hints": show_hints,
            "can_view_reference": False,
            "completed": True,
            "completion_summary": {
                "total_score": session.total_score,
                "average_score": session.average_score,
                "completed_turns": session.completed_turns,
            },
        }

    current_turn_number = session.start_turn + session.completed_turns
    turn = get_turn(session.scenario_id, current_turn_number)
    if not turn:
        raise HTTPException(status_code=404, detail="Turn not found")

    return {
        "session_id": session.id,
        "scenario_id": session.scenario_id,
        "scenario_title": session.scenario_title,
        "description": scenario["description"],
        "difficulty": session.difficulty,
        "category": session.category,
        "mode": session.mode,
        "turn_number": current_turn_number,
        "total_turns": session.total_turns,
        "speaker_line": turn["speaker_line"],
        "task_label": turn.get("intent"),
        "task_breakdown": turn.get("task_breakdown", []) if show_hints else [],
        "keywords": turn.get("keywords", []) if show_hints else [],
        "sentence_frames": turn.get("sentence_frames", []) if show_hints else [],
        "reference_answers": turn.get("reference_answers", []) if show_hints else [],
        "recommended_phrases": turn.get("recommended_phrases", []) if show_hints else [],
        "progress_text": f"第 {current_turn_number} 轮 · 本次剩余 {session.total_turns - session.completed_turns} 轮",
        "show_hints": show_hints,
        "can_view_reference": show_hints and bool(turn.get("reference_answers")),
        "completed": False,
        "completion_summary": None,
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    scenarios = list_scenarios()
    categories = get_categories()
    completed_sessions = [session for session in crud.list_sessions(db) if session.is_completed]
    context = _page_context(request, db)
    context.update(
        {
            "scenario_count": len(scenarios),
            "completed_count": len(completed_sessions),
            "categories": categories,
        }
    )
    return templates.TemplateResponse(request, "home.html", context)


@app.get("/scenarios", response_class=HTMLResponse)
def scenarios_page(
    request: Request,
    difficulty: str = "all",
    category: str = "all",
    db: Session = Depends(get_db),
):
    context = _page_context(request, db)
    context.update(
        {
            "scenarios": list_scenarios(difficulty=difficulty, category=category),
            "difficulty": difficulty,
            "category": category,
            "categories": get_categories(),
        }
    )
    return templates.TemplateResponse(request, "scenarios.html", context)


@app.get("/scenarios/{scenario_id}/mode", response_class=HTMLResponse)
def mode_page(scenario_id: str, request: Request, db: Session = Depends(get_db)):
    scenario = get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    context = _page_context(request, db)
    context["scenario"] = scenario
    return templates.TemplateResponse(request, "mode_select.html", context)


@app.post("/scenarios/{scenario_id}/start")
def start_session(
    scenario_id: str,
    mode: str = Form(...),
    start_turn: int = Form(default=1),
    db: Session = Depends(get_db),
):
    scenario = get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    session = crud.create_session(db, scenario, mode, start_turn=start_turn)
    return RedirectResponse(url=f"/train/{session.id}", status_code=303)


@app.get("/train/{session_id}", response_class=HTMLResponse)
def training_page(session_id: int, request: Request, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    scenario = get_scenario(session.scenario_id)
    context = _page_context(request, db)
    context.update({"session": session, "scenario": scenario})
    return templates.TemplateResponse(request, "training.html", context)


@app.get("/mistakes", response_class=HTMLResponse)
def mistakes_page(request: Request, db: Session = Depends(get_db)):
    context = _page_context(request, db)
    mistake_rows = []
    for mistake in crud.list_mistake_notes(db):
        source_session = crud.get_session(db, mistake.session_id)
        scenario = get_scenario_by_title(mistake.scenario_title)
        mistake_rows.append(
            {
                "mistake": mistake,
                "source_session": source_session,
                "scenario_id": scenario["id"] if scenario else None,
            }
        )
    context["mistake_rows"] = mistake_rows
    return templates.TemplateResponse(request, "mistakes.html", context)


@app.get("/mistakes/{mistake_id}/retry")
def retry_mistake(mistake_id: int, mode: str = "learning", db: Session = Depends(get_db)):
    mistake = crud.get_mistake_note(db, mistake_id)
    if not mistake:
        raise HTTPException(status_code=404, detail="Mistake not found")
    scenario = get_scenario_by_title(mistake.scenario_title)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    session = crud.create_session(db, scenario, mode, start_turn=mistake.turn_number)
    return RedirectResponse(url=f"/train/{session.id}", status_code=303)


@app.get("/records", response_class=HTMLResponse)
def records_page(request: Request, db: Session = Depends(get_db)):
    sessions = crud.list_sessions(db)
    session_rows = []
    for session in sessions:
        turns = crud.list_session_turns(db, session.id)
        turn_scores = [turn.total_score for turn in turns if turn.passed]
        session_rows.append(
            {
                "session": session,
                "turn_scores": turn_scores,
                "attempt_count": len(turns),
            }
        )

    context = _page_context(request, db)
    context["session_rows"] = session_rows
    return templates.TemplateResponse(request, "records.html", context)


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db)):
    context = _page_context(request, db)
    return templates.TemplateResponse(request, "settings.html", context)


@app.post("/settings")
def update_settings(
    default_mode: str = Form(...),
    difficulty_filter: str = Form(...),
    show_hints: str | None = Form(default=None),
    save_low_scores: str | None = Form(default=None),
    low_score_threshold: int = Form(...),
    db: Session = Depends(get_db),
):
    crud.update_settings(
        db,
        {
            "default_mode": default_mode,
            "difficulty_filter": difficulty_filter,
            "show_hints": show_hints == "on",
            "save_low_scores": save_low_scores == "on",
            "low_score_threshold": low_score_threshold,
        },
    )
    return RedirectResponse(url="/settings", status_code=303)


@app.get("/analytics", response_class=HTMLResponse)
def analytics_page(request: Request, db: Session = Depends(get_db)):
    analysis = build_weakness_analysis(crud.list_all_turns(db), crud.list_mistake_notes(db))
    context = _page_context(request, db)
    context["analysis"] = analysis
    return templates.TemplateResponse(request, "analytics.html", context)


@app.get("/api/sessions/{session_id}/state", response_class=JSONResponse)
def get_session_state(session_id: int, db: Session = Depends(get_db)):
    return JSONResponse(_build_turn_state(db, session_id))


@app.post("/api/sessions/{session_id}/submit", response_class=JSONResponse)
def submit_turn(session_id: int, payload: ResponseSubmission, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.is_completed:
        return JSONResponse(
            {
                "passed": True,
                "completed": True,
                "can_continue": False,
                "total_score": session.total_score,
                "scores": {},
                "dimension_feedback": {},
                "fragment_issues": [],
                "summary": "该练习已完成。",
                "detailed_feedback": "",
                "correction": {},
                "recommendation": {},
                "reference_answers": [],
                "mode": session.mode,
                "issue_tags": [],
                "low_dimensions": [],
                "next_turn_available": False,
                "completion_summary": {
                    "total_score": session.total_score,
                    "average_score": session.average_score,
                },
            }
        )

    turn_number = session.start_turn + session.completed_turns
    turn = get_turn(session.scenario_id, turn_number)
    if not turn:
        raise HTTPException(status_code=404, detail="Turn not found")

    score_result = evaluate_response(payload.response_text, turn, session.mode)
    correction, recommendation = generate_feedback(payload.response_text, turn, session.mode, score_result)
    public_correction = {
        key: value
        for key, value in correction.items()
        if key not in {"natural_version", "formal_version"}
    }

    passed = True
    if session.mode == "practice":
        passed = (
            score_result.total_score >= 30
            and score_result.scores["敬语准确度"] >= 6
            and score_result.scores["场景适配度"] >= 6
        )

    attempt = crud.create_turn_attempt(
        db,
        session=session,
        turn_number=turn_number,
        prompt=turn["speaker_line"],
        response=payload.response_text,
        score_result=score_result,
        correction=public_correction,
        recommendation=recommendation,
        passed=passed,
    )

    settings = crud.get_or_create_settings(db)
    if settings.save_low_scores and (
        score_result.total_score <= settings.low_score_threshold or score_result.low_dimensions
    ):
        crud.save_mistake_note(
            db,
            session=session,
            practice_turn_id=attempt.id,
            turn_number=turn_number,
            response=payload.response_text,
            low_dimensions=score_result.low_dimensions,
            issue_tags=score_result.issue_tags,
            recommended_expression=recommendation["recommended_expression"],
        )

    completion_summary = None
    if passed:
        session = crud.advance_session(db, session, score_result.total_score)
        if session.is_completed:
            completion_summary = {
                "total_score": session.total_score,
                "average_score": session.average_score,
                "completed_turns": session.completed_turns,
            }

    return JSONResponse(
        {
            "passed": passed,
            "completed": session.is_completed,
            "can_continue": passed and not session.is_completed,
            "total_score": score_result.total_score,
            "scores": score_result.scores,
            "dimension_feedback": score_result.dimension_feedback,
            "fragment_issues": score_result.fragment_issues,
            "summary": score_result.summary,
            "detailed_feedback": score_result.detailed_feedback,
            "correction": public_correction,
            "recommendation": recommendation,
            "reference_answers": turn.get("reference_answers", []),
            "mode": session.mode,
            "issue_tags": score_result.issue_tags,
            "low_dimensions": score_result.low_dimensions,
            "next_turn_available": passed and not session.is_completed,
            "completion_summary": completion_summary,
        }
    )
