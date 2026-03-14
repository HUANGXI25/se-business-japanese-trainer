from fastapi.testclient import TestClient

import main
from scenario_loader import load_scenarios
from scoring_engine import score_response


def test_scenarios_load_successfully() -> None:
    scenarios = load_scenarios()

    assert len(scenarios) >= 20
    first = scenarios[0]
    assert first["id"]
    assert first["title"]
    assert 3 <= len(first["turns"]) <= 5


def test_scoring_engine_reference_answer_scores_reasonably() -> None:
    scenario = load_scenarios()[0]
    turn = scenario["turns"][0]
    response = turn["reference_answers"][0]

    result = score_response(response, turn, mode="learning")

    assert result.total_score >= 30
    assert result.scores["敬语准确度"] >= 6
    assert result.summary


def test_main_module_imports() -> None:
    assert main.app.title == "Business Japanese SE Roleplay Trainer"


def test_homepage_smoke() -> None:
    client = TestClient(main.app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Business Japanese SE Roleplay Trainer" in response.text


def test_learning_mode_training_flow_returns_feedback() -> None:
    client = TestClient(main.app)
    scenario = load_scenarios()[0]

    start_response = client.post(
        f"/scenarios/{scenario['id']}/start",
        data={"mode": "learning", "start_turn": 1},
        follow_redirects=False,
    )

    assert start_response.status_code == 303
    train_url = start_response.headers["location"]
    session_id = int(train_url.rsplit("/", 1)[-1])

    training_page = client.get(train_url)
    assert training_page.status_code == 200
    assert scenario["title"] in training_page.text

    state_response = client.get(f"/api/sessions/{session_id}/state")
    state = state_response.json()
    assert state["mode"] == "learning"
    assert state["show_hints"] is True
    assert len(state["task_breakdown"]) >= 1

    submit_response = client.post(
        f"/api/sessions/{session_id}/submit",
        json={"response_text": scenario["turns"][0]["reference_answers"][0]},
    )
    result = submit_response.json()

    assert submit_response.status_code == 200
    assert result["total_score"] > 0
    assert "recommendation" in result
    assert result["recommendation"]["recommended_expression"]
    assert result["can_continue"] is True


def test_practice_mode_hides_learning_hints_in_state() -> None:
    client = TestClient(main.app)
    scenario = load_scenarios()[0]

    start_response = client.post(
        f"/scenarios/{scenario['id']}/start",
        data={"mode": "practice", "start_turn": 1},
        follow_redirects=False,
    )
    session_id = int(start_response.headers["location"].rsplit("/", 1)[-1])

    state_response = client.get(f"/api/sessions/{session_id}/state")
    state = state_response.json()

    assert state["mode"] == "practice"
    assert state["show_hints"] is False
    assert state["task_breakdown"] == []
    assert state["reference_answers"] == []


def test_records_page_shows_created_practice_session() -> None:
    client = TestClient(main.app)
    scenario = load_scenarios()[0]

    start_response = client.post(
        f"/scenarios/{scenario['id']}/start",
        data={"mode": "learning", "start_turn": 1},
        follow_redirects=False,
    )
    session_id = int(start_response.headers["location"].rsplit("/", 1)[-1])

    client.post(
        f"/api/sessions/{session_id}/submit",
        json={"response_text": scenario["turns"][0]["reference_answers"][0]},
    )

    records_response = client.get("/records")

    assert records_response.status_code == 200
    assert "历史训练记录" in records_response.text
    assert scenario["title"] in records_response.text
