from __future__ import annotations

from scoring_engine import CASUAL_RULES, ScoreResult


KEIGO_RULES = [
    {
        "pattern": "わかりました",
        "replacement": "承知いたしました",
        "reason": "在对上司、客户或跨团队沟通中，使用更郑重的敬语更自然。",
        "tag": "敬语等级错误",
    },
    {
        "pattern": "すみません",
        "replacement": "申し訳ございません",
        "reason": "商务致歉场景更适合使用正式道歉表达。",
        "tag": "商务套语使用不当",
    },
    {
        "pattern": "ちょっと",
        "replacement": "少々",
        "reason": "“ちょっと”偏口语，正式场景中建议改成“少々”或直接说明原因。",
        "tag": "语气太随便",
    },
    {
        "pattern": "教えてください",
        "replacement": "ご教示いただけますでしょうか",
        "reason": "向上司、客户请求信息时，建议使用更正式的请求句式。",
        "tag": "表达不商务",
    },
    {
        "pattern": "見てください",
        "replacement": "ご確認いただけますでしょうか",
        "reason": "商务场景中“見てください”过于直接，改成依赖表达更自然。",
        "tag": "表达不商务",
    },
    {
        "pattern": "やります",
        "replacement": "対応いたします",
        "reason": "在 SE 工作沟通里，用“対応いたします”更符合任务执行语境。",
        "tag": "用词不商务",
    },
]


def _rewrite_text(text: str) -> str:
    rewritten = text.strip()
    for pattern, replacement in CASUAL_RULES.items():
        rewritten = rewritten.replace(pattern, replacement)
    return rewritten


def generate_correction(response: str, turn: dict, score_result: ScoreResult, mode: str) -> dict:
    issues = []
    suggestions = []
    seen_fragments = set()

    for item in score_result.fragment_issues:
        fragment_key = (item["fragment"], item["problem_type"])
        if fragment_key in seen_fragments:
            continue
        seen_fragments.add(fragment_key)
        issues.append(
            {
                "fragment": item["fragment"],
                "type": item["problem_type"],
                "reason": item["reason"],
                "message": f"命中片段「{item['fragment']}」：{item['reason']}",
                "replacement": item["replacement"],
            }
        )
        suggestions.append(
            {
                "original": item["fragment"],
                "problem_type": item["problem_type"],
                "reason": item["reason"],
                "replacement": item["replacement"],
            }
        )

    for rule in KEIGO_RULES:
        if rule["pattern"] in response and (rule["pattern"], rule["tag"]) not in seen_fragments:
            issues.append(
                {
                    "fragment": rule["pattern"],
                    "type": rule["tag"],
                    "reason": rule["reason"],
                    "message": f"“{rule['pattern']}”在当前场景下不够正式。",
                    "replacement": rule["replacement"],
                }
            )
            suggestions.append(
                {
                    "original": rule["pattern"],
                    "problem_type": rule["tag"],
                    "reason": rule["reason"],
                    "replacement": rule["replacement"],
                }
            )

    if score_result.missing_keywords and "场景关键动作缺失" not in {item["type"] for item in issues}:
        issues.append(
            {
                "fragment": "关键信息",
                "type": "场景信息缺失",
                "reason": f"当前回答没有明确覆盖：{'、'.join(score_result.missing_keywords)}。",
                "message": f"当前回答没有明确覆盖：{'、'.join(score_result.missing_keywords)}。",
                "replacement": "补入缺失关键词并明确说明状态、原因或请求。",
            }
        )
        suggestions.append(
            {
                "original": "句子整体",
                "problem_type": "场景信息缺失",
                "reason": "该轮目标要求回答关键动作或信息点，否则会显得沟通不完整。",
                "replacement": "可补入缺失关键词并明确说明状态、原因或请求。",
            }
        )

    if "？" not in response and "か" not in response and "確認" in turn.get("intent", ""):
        issues.append(
            {
                "fragment": "句末表达",
                "type": "确认动作不明确",
                "reason": "这是确认类场景，但当前句子没有明确提出确认请求。",
                "message": "这是确认类场景，但当前句子没有明确提出确认请求。",
                "replacement": "使用「〜でよろしいでしょうか」或「ご確認いただけますでしょうか」。",
            }
        )
        suggestions.append(
            {
                "original": "句末表达",
                "problem_type": "确认动作不明确",
                "reason": "确认类场景需要把“请确认”的动作说出来，否则会变成单向说明。",
                "replacement": "使用「〜でよろしいでしょうか」或「ご確認いただけますでしょうか」。",
            }
        )

    natural_version = _rewrite_text(response)
    if natural_version == response.strip():
        natural_version = turn.get("reference_answers", [""])[-1]

    formal_version = turn.get("reference_answers", [""])[0]
    if not formal_version:
        formal_version = natural_version

    tone = "学习模式下建议先确保意图完整，再逐步调整敬语细节。" if mode == "learning" else "实战模式下需要同时兼顾敬语、完整度和商务自然度。"

    return {
        "issues": issues,
        "suggestions": suggestions,
        "natural_version": natural_version,
        "formal_version": formal_version,
        "coaching_note": tone,
    }
