from __future__ import annotations

import json
from collections import Counter


DIMENSION_FIELD_MAP = {
    "敬语准确度": "keigo_score",
    "商务自然度": "business_score",
    "场景适配度": "scenario_fit_score",
    "表达逻辑": "logic_score",
    "回答完整度": "completeness_score",
}


def build_weakness_analysis(turns: list, mistake_notes: list) -> dict:
    if not turns:
        return {
            "average_scores": {},
            "weaknesses": ["暂无练习数据。完成几轮训练后，这里会显示你的薄弱点统计。"],
            "top_issue_tags": [],
            "mode_breakdown": {},
        }

    average_scores = {}
    for label, field_name in DIMENSION_FIELD_MAP.items():
        values = [getattr(turn, field_name) for turn in turns]
        average_scores[label] = round(sum(values) / len(values), 1)

    weaknesses = []
    for label, value in sorted(average_scores.items(), key=lambda item: item[1]):
        if value <= 6:
            weaknesses.append(f"{label}偏弱，建议优先复习相关错题。")

    if not weaknesses:
        weaknesses.append("当前各维度表现较均衡，建议继续提升正式表达和稳定度。")

    tag_counter = Counter()
    for note in mistake_notes:
        for tag in note.issue_tags.split(","):
            if tag:
                tag_counter[tag] += 1

    if not tag_counter:
        for turn in turns:
            try:
                issue_tags = json.loads(turn.issue_tags)
            except json.JSONDecodeError:
                issue_tags = []
            for tag in issue_tags:
                tag_counter[tag] += 1

    mode_counter = Counter(turn.mode for turn in turns)
    return {
        "average_scores": average_scores,
        "weaknesses": weaknesses,
        "top_issue_tags": tag_counter.most_common(5),
        "mode_breakdown": dict(mode_counter),
    }
