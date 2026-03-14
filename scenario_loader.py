import json
from functools import lru_cache
from pathlib import Path


SCENARIO_FILE = Path(__file__).parent / "data" / "scenarios.json"


@lru_cache(maxsize=1)
def load_scenarios() -> list[dict]:
    with SCENARIO_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def list_scenarios(difficulty: str | None = None, category: str | None = None) -> list[dict]:
    scenarios = load_scenarios()
    filtered = scenarios
    if difficulty and difficulty != "all":
        filtered = [item for item in filtered if item["difficulty"] == difficulty]
    if category and category != "all":
        filtered = [item for item in filtered if item["category"] == category]
    return filtered


def get_scenario(scenario_id: str) -> dict | None:
    for scenario in load_scenarios():
        if scenario["id"] == scenario_id:
            return scenario
    return None


def get_scenario_by_title(title: str) -> dict | None:
    for scenario in load_scenarios():
        if scenario["title"] == title:
            return scenario
    return None


def get_categories() -> list[str]:
    return sorted({scenario["category"] for scenario in load_scenarios()})


def get_turn(scenario_id: str, turn_number: int) -> dict | None:
    scenario = get_scenario(scenario_id)
    if not scenario:
        return None
    turns = scenario.get("turns", [])
    if 1 <= turn_number <= len(turns):
        turn = dict(turns[turn_number - 1])
        turn["listener_type"] = turn.get("listener_type") or scenario.get("listener_type", "colleague")
        turn["scenario_title"] = scenario.get("title")
        turn["category"] = scenario.get("category")
        return turn
    return None
