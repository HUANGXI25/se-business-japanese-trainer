from __future__ import annotations

from correction_engine import generate_correction
from recommendation_engine import generate_recommendation
from scoring_engine import score_response


def evaluate_response(response: str, turn: dict, mode: str):
    return score_response(response, turn, mode)


def generate_feedback(response: str, turn: dict, mode: str, score_result):
    correction = generate_correction(response, turn, score_result, mode)
    recommendation = generate_recommendation(response, turn, score_result, correction)
    return correction, recommendation


def rewrite_business_japanese(response: str, turn: dict, mode: str) -> dict:
    score_result = score_response(response, turn, mode)
    correction = generate_correction(response, turn, score_result, mode)
    return {
        "natural_version": correction["natural_version"],
        "formal_version": correction["formal_version"],
    }
