from __future__ import annotations

from scoring_engine import ScoreResult

LISTENER_LABELS = {
    "manager": "上司",
    "client": "客户",
    "colleague": "同事",
}


def _adapt_style(expression: str, listener_type: str) -> str:
    rewritten = expression.strip()
    if not rewritten:
        return rewritten

    if listener_type == "client":
        rewritten = rewritten.replace("時間のあるときに", "お手すきの際に")
        rewritten = rewritten.replace("見てもらえると助かります", "ご確認いただけますと幸いです")
        rewritten = rewritten.replace("共有します", "共有いたします")
        return rewritten

    if listener_type == "colleague":
        rewritten = rewritten.replace("ご確認いただけますでしょうか", "確認してもらえると助かります")
        rewritten = rewritten.replace("お手すきの際に", "時間のあるときに")
        rewritten = rewritten.replace("ご案内いたします", "共有します")
        rewritten = rewritten.replace("進めてまいります", "進めます")
        return rewritten

    return rewritten


def _style_note(listener_type: str) -> str:
    if listener_type == "client":
        return "对客户建议使用更郑重的缓冲表达、确认表达和说明语气。"
    if listener_type == "manager":
        return "对上司建议保持正式、简洁，优先结论和当前判断。"
    return "对同事建议保持职业化和清晰度，不必过度隆重，但要把信息说完整。"


def generate_recommendation(response: str, turn: dict, score_result: ScoreResult, correction: dict) -> dict:
    listener_type = turn.get("listener_type", "colleague")
    base_expression = (
        turn.get("recommended_expression")
        or turn.get("reference_answers", [""])[0]
        or correction.get("formal_version")
        or correction.get("natural_version")
        or response.strip()
    )
    recommended_expression = _adapt_style(base_expression, listener_type)

    return {
        "listener_type": listener_type,
        "listener_label": LISTENER_LABELS.get(listener_type, "沟通对象"),
        "recommended_expression": recommended_expression,
        "style_note": _style_note(listener_type),
        "next_action": "下一次可以先说结论，再补充原因和请求，这样更符合职场沟通节奏。",
    }
