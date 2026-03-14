from __future__ import annotations

from dataclasses import dataclass


BUSINESS_PHRASES = [
    "承知いたしました",
    "かしこまりました",
    "申し訳ございません",
    "恐れ入りますが",
    "お手数をおかけしますが",
    "ご確認いただけますでしょうか",
    "ご共有いたします",
    "ご連絡いたします",
    "現状",
    "進捗",
    "対応いたします",
    "確認いたしました",
    "ご相談させていただきたく",
]

CASUAL_RULES = {
    "わかりました": "承知いたしました",
    "すみません": "申し訳ございません",
    "ちょっと": "少々",
    "できません": "対応が難しい状況です",
    "あとで": "後ほど",
    "いいですか": "よろしいでしょうか",
    "教えてください": "ご教示いただけますでしょうか",
    "見てください": "ご確認いただけますでしょうか",
    "無理です": "難しい状況です",
    "やります": "対応いたします",
}

LOGIC_MARKERS = ["まず", "現状", "そのため", "つきましては", "なお", "また", "ため", "ので", "現時点", "本日中"]
POLITE_ENDINGS = ["ます", "ました", "でしょうか", "ございます", "いたします", "いたしました", "させていただきます"]
INTENT_KEYWORDS = [
    (["汇报", "进度", "状态"], ["進捗", "現状", "完了", "対応"]),
    (["延期", "延迟", "致歉", "道歉"], ["遅れ", "理由", "見込み", "申し訳"]),
    (["确认", "认知", "需求"], ["確認", "認識", "要件", "ご確認"]),
    (["致歉", "道歉", "误解"], ["申し訳", "お詫び", "失礼"]),
    (["请求", "协助", "审阅"], ["お願い", "ご確認", "ご対応", "ご教示", "レビュー"]),
    (["风险", "懸念"], ["懸念", "影響", "リスク", "対応策"]),
]


@dataclass
class ScoreResult:
    scores: dict[str, int]
    total_score: int
    summary: str
    detailed_feedback: str
    dimension_feedback: dict[str, str]
    dimension_issues: dict[str, list[dict[str, str]]]
    fragment_issues: list[dict[str, str]]
    matched_keywords: list[str]
    missing_keywords: list[str]
    casual_hits: list[str]
    business_hits: list[str]
    issue_tags: list[str]
    low_dimensions: list[str]


def _clamp(score: int) -> int:
    return max(0, min(10, score))


def _contains_any(text: str, patterns: list[str]) -> int:
    return sum(1 for pattern in patterns if pattern in text)


def _sample(items: list[str], limit: int = 3) -> str:
    return "、".join(items[:limit])


def _infer_intent_bonus(intent: str, response: str) -> int:
    for markers, values in INTENT_KEYWORDS:
        if any(marker in intent for marker in markers):
            return 1 if any(word in response for word in values) else 0
    return 0


def _add_issue(
    issues: dict[str, list[dict[str, str]]],
    dimension: str,
    fragment: str,
    problem_type: str,
    reason: str,
    replacement: str,
) -> None:
    issues.setdefault(dimension, []).append(
        {
            "fragment": fragment,
            "problem_type": problem_type,
            "reason": reason,
            "replacement": replacement,
        }
    )


def _build_fragment_issues(
    text: str,
    turn: dict,
    matched_keywords: list[str],
    missing_keywords: list[str],
    casual_hits: list[str],
    has_polite_ending: bool,
    logic_hits: int,
) -> dict[str, list[dict[str, str]]]:
    issues: dict[str, list[dict[str, str]]] = {
        "敬语准确度": [],
        "商务自然度": [],
        "场景适配度": [],
        "回答完整度": [],
        "表达逻辑": [],
    }

    for hit in casual_hits:
        replacement = CASUAL_RULES.get(hit, "请改成更正式的商务表达")
        reason = f"「{hit}」在当前商务场景下偏口语，会削弱正式感。"
        _add_issue(issues, "敬语准确度", hit, "口语化表达", reason, replacement)
        _add_issue(issues, "商务自然度", hit, "不够商务", reason, replacement)

    recommended_phrases = turn.get("recommended_phrases", [])
    if not any(phrase in text for phrase in recommended_phrases[:3]) and recommended_phrases:
        _add_issue(
            issues,
            "商务自然度",
            "回答整体",
            "商务套语使用不足",
            "这句话能表达意思，但缺少该场景常见的商务套语，听起来会偏直接。",
            f"可考虑补入「{recommended_phrases[0]}」",
        )

    if "よろしく" in text and "お願いいたします" not in text:
        _add_issue(
            issues,
            "商务自然度",
            "よろしく",
            "商务套语不足",
            "单独使用「よろしく」偏随手，正式场景里分量不够。",
            "よろしくお願いいたします",
        )

    if not has_polite_ending:
        _add_issue(
            issues,
            "敬语准确度",
            "句末表达",
            "敬体不足",
            "句末没有稳定落在「〜ます / 〜いたします」这类敬体上。",
            "将句末改成「〜しております」「〜いたします」",
        )

    for keyword in missing_keywords[:3]:
        replacement = f"补入包含「{keyword}」的信息，明确状态、原因或请求。"
        reason = f"当前回答没有提到「{keyword}」，对方可能无法判断你是否完成了该场景动作。"
        _add_issue(issues, "场景适配度", f"未提及：{keyword}", "场景关键动作缺失", reason, replacement)
        _add_issue(issues, "回答完整度", f"未提及：{keyword}", "信息不完整", reason, replacement)

    if "确认" in turn.get("intent", "") and "？" not in text and "か" not in text and "でしょうか" not in text:
        _add_issue(
            issues,
            "场景适配度",
            "确认动作",
            "确认句式缺失",
            "这是确认类场景，但你的句子里没有明确提出确认请求。",
            "使用「〜でよろしいでしょうか」「ご確認いただけますでしょうか」",
        )

    if ("致歉" in turn.get("intent", "") or "延期" in turn.get("intent", "")) and "申し訳" not in text and "お詫び" not in text:
        _add_issue(
            issues,
            "场景适配度",
            "致歉动作",
            "必要动作缺失",
            "这一轮需要先致歉，但当前回答没有明确的道歉表达。",
            "先补上「申し訳ございません」或「お詫び申し上げます」",
        )

    if ("风险" in turn.get("intent", "") or "懸念" in turn.get("intent", "")) and "懸念" not in text and "影響" not in text:
        _add_issue(
            issues,
            "场景适配度",
            "风险说明",
            "关键动作缺失",
            "这是风险汇报场景，但你没有明确说出懸念点或影响范围。",
            "补上「懸念がございます」「〜への影響があります」",
        )

    if len(text) < 18:
        _add_issue(
            issues,
            "回答完整度",
            "回答整体",
            "信息量不足",
            "回答偏短，通常只说到了结论，没有把原因、影响或下一步交代清楚。",
            "至少补一句原因、影响或下一步安排",
        )

    if logic_hits == 0:
        _add_issue(
            issues,
            "表达逻辑",
            "句子连接",
            "结构提示不足",
            "缺少「まず」「現時点では」「そのため」等连接提示，信息顺序不够清楚。",
            "先说结论，再用连接词补充原因或下一步",
        )

    if not matched_keywords:
        _add_issue(
            issues,
            "场景适配度",
            "回答整体",
            "贴题度不足",
            "回答没有命中本轮核心关键词，对方难以判断你是否在回应当前场景。",
            "围绕本轮任务拆解里的动作重新组织一句完整回答",
        )

    return issues


def _build_dimension_feedback(
    label: str,
    score: int,
    positives: list[str],
    issues: list[dict[str, str]],
    fallback_improvement: str,
) -> str:
    positive_text = "；".join(positives) if positives else "已经给出了基本可理解的回应"
    if issues:
        primary = issues[0]
        issue_text = (
            f"命中片段「{primary['fragment']}」，问题是{primary['problem_type']}；"
            f"{primary['reason']} 建议改成：{primary['replacement']}。"
        )
    else:
        issue_text = f"这一维没有明显的规则型扣分点，建议继续保持。"
    return f"{positive_text}。{issue_text if score < 10 or issues else issue_text} 如要继续提升，可优先：{fallback_improvement}。"


def score_response(response: str, turn: dict, mode: str) -> ScoreResult:
    text = response.strip()
    if not text:
        scores = {
            "敬语准确度": 0,
            "商务自然度": 0,
            "场景适配度": 0,
            "表达逻辑": 0,
            "回答完整度": 0,
        }
        return ScoreResult(
            scores=scores,
            total_score=0,
            summary="回答为空，无法进入有效评分。",
            detailed_feedback="请至少用一句完整的日语进行回复。",
            dimension_feedback={label: "没有提交有效回答，因此这一维无法得分。建议先用完整敬体句说明你的状态或请求。" for label in scores},
            dimension_issues={label: [] for label in scores},
            fragment_issues=[],
            matched_keywords=[],
            missing_keywords=turn.get("keywords", []),
            casual_hits=[],
            business_hits=[],
            issue_tags=["empty_response"],
            low_dimensions=list(scores.keys()),
        )

    scoring_keywords = turn.get("scoring_keywords") or turn.get("keywords", [])
    keywords = scoring_keywords
    matched_keywords = [keyword for keyword in keywords if keyword in text]
    missing_keywords = [keyword for keyword in keywords if keyword not in text]
    casual_hits = [pattern for pattern in CASUAL_RULES if pattern in text]
    business_hits = [phrase for phrase in BUSINESS_PHRASES if phrase in text]
    logic_hits = _contains_any(text, LOGIC_MARKERS)
    polite_hits = _contains_any(text, POLITE_ENDINGS)
    intent_bonus = _infer_intent_bonus(turn.get("intent", ""), text)
    length_bonus = 2 if len(text) >= 30 else 1 if len(text) >= 18 else 0
    keyword_ratio = len(matched_keywords) / max(1, len(keywords))
    has_polite_ending = polite_hits > 0 or text.endswith("です") or text.endswith("ます")

    keigo = 4 + min(3, polite_hits) + min(2, len(business_hits)) - (2 * len(casual_hits))
    if not has_polite_ending:
        keigo -= 2

    business = 4 + min(3, len(business_hits)) + int(keyword_ratio * 2) - (2 * len(casual_hits))
    if "よろしく" in text and "お願いいたします" not in text:
        business -= 1

    scenario_fit = 3 + int(keyword_ratio * 5) + intent_bonus + (1 if turn.get("speaker_line", "")[:2] in text else 0)
    logic = 4 + min(3, logic_hits) + length_bonus
    completeness = 3 + int(keyword_ratio * 4) + length_bonus + intent_bonus
    if len(text) < 12:
        completeness -= 2

    if mode == "practice":
        if casual_hits:
            keigo -= 1
            business -= 1
        if len(matched_keywords) < max(1, len(keywords) // 2):
            scenario_fit -= 1
            completeness -= 1
    else:
        if keigo < 4:
            keigo += 1
        if business < 4:
            business += 1

    scores = {
        "敬语准确度": _clamp(keigo),
        "商务自然度": _clamp(business),
        "场景适配度": _clamp(scenario_fit),
        "表达逻辑": _clamp(logic),
        "回答完整度": _clamp(completeness),
    }
    total_score = sum(scores.values())

    issue_tags: list[str] = []
    if casual_hits:
        issue_tags.append("口语化")
    if scores["敬语准确度"] <= 5:
        issue_tags.append("敬语不足")
    if scores["商务自然度"] <= 5:
        issue_tags.append("商务表达不自然")
    if scores["场景适配度"] <= 5:
        issue_tags.append("关键信息缺失")
    if scores["表达逻辑"] <= 5:
        issue_tags.append("逻辑连接偏弱")
    if scores["回答完整度"] <= 5:
        issue_tags.append("回答不完整")

    if total_score >= 42:
        summary = "整体表达成熟，适合正式商务场景。"
    elif total_score >= 34:
        summary = "整体可用，但还有一些商务表达和完整度可以加强。"
    elif total_score >= 25:
        summary = "基本意图已传达，但在敬语、逻辑或完整度上仍较明显不足。"
    else:
        summary = "当前回答较难直接用于商务场景，建议先根据反馈修改后再练习。"

    detail_parts = []
    if matched_keywords:
        detail_parts.append(f"已覆盖关键词：{'、'.join(matched_keywords)}。")
    if missing_keywords:
        detail_parts.append(f"缺少关键词：{'、'.join(missing_keywords)}。")
    if casual_hits:
        detail_parts.append(f"检测到偏口语表达：{'、'.join(casual_hits)}。")
    if not detail_parts:
        detail_parts.append("表达较完整，没有检测到明显的规则型问题。")

    low_dimensions = [name for name, score in scores.items() if score <= 6]
    dimension_issues = _build_fragment_issues(
        text=text,
        turn=turn,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        casual_hits=casual_hits,
        has_polite_ending=has_polite_ending,
        logic_hits=logic_hits,
    )
    positives_by_dimension = {
        "敬语准确度": [
            item for item in [
                f"使用了正式表达「{_sample(business_hits, 2)}」" if business_hits else "",
                "句末保持在敬体" if has_polite_ending else "",
            ] if item
        ],
        "商务自然度": [
            item for item in [
                f"用了商务表达「{_sample(business_hits, 2)}」" if business_hits else "",
                f"命中了业务关键词「{_sample(matched_keywords, 2)}」" if matched_keywords else "",
            ] if item
        ],
        "场景适配度": [
            item for item in [
                f"覆盖了场景核心点「{_sample(matched_keywords, 3)}」" if matched_keywords else "",
            ] if item
        ],
        "表达逻辑": [
            item for item in [
                "句子长度足够承载结论和补充信息" if len(text) >= 24 else "",
                "有使用结构提示词" if logic_hits > 0 else "",
            ] if item
        ],
        "回答完整度": [
            item for item in [
                "回答长度足够，不只是短句回应" if len(text) >= 24 else "",
                f"已覆盖必要信息「{_sample(matched_keywords, 2)}」" if matched_keywords else "",
            ] if item
        ],
    }
    dimension_feedback = {
        label: _build_dimension_feedback(
            label=label,
            score=score,
            positives=positives_by_dimension.get(label, []),
            issues=dimension_issues.get(label, []),
            fallback_improvement={
                "敬语准确度": "统一使用更正式的敬语词和句末",
                "商务自然度": "把口语词替换成商务套语，并保持结论先行",
                "场景适配度": "补上场景要求的动作、原因或确认请求",
                "表达逻辑": "先说结论，再说原因和下一步",
                "回答完整度": "把现状、原因和后续动作说完整",
            }[label],
        )
        for label, score in scores.items()
    }
    fragment_issues = []
    for items in dimension_issues.values():
        for item in items:
            if item not in fragment_issues:
                fragment_issues.append(item)

    return ScoreResult(
        scores=scores,
        total_score=total_score,
        summary=summary,
        detailed_feedback=" ".join(detail_parts),
        dimension_feedback=dimension_feedback,
        dimension_issues=dimension_issues,
        fragment_issues=fragment_issues,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        casual_hits=casual_hits,
        business_hits=business_hits,
        issue_tags=issue_tags,
        low_dimensions=low_dimensions,
    )
