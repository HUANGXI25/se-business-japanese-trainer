async function fetchJson(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });
    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
}

function createListItems(container, values, formatter) {
    container.innerHTML = "";
    if (!values || values.length === 0) {
        const item = document.createElement("li");
        item.textContent = "本轮未检测到对应内容。";
        container.appendChild(item);
        return;
    }
    values.forEach((value) => {
        const item = document.createElement("li");
        item.innerHTML = formatter(value);
        container.appendChild(item);
    });
}

function renderTurnState(state) {
    const progressText = document.getElementById("progress-text");
    const speakerLine = document.getElementById("speaker-line");
    const hintPanel = document.getElementById("hint-panel");
    const practiceNote = document.getElementById("practice-note");
    const hintNoteTitle = document.getElementById("hint-note-title");
    const hintNoteText = document.getElementById("hint-note-text");
    const taskLabel = document.getElementById("task-label");
    const taskBreakdownList = document.getElementById("task-breakdown-list");
    const keywordList = document.getElementById("keyword-list");
    const frameList = document.getElementById("frame-list");
    const referenceList = document.getElementById("reference-list");
    const referenceDetails = document.getElementById("reference-details");
    const responseInput = document.getElementById("response-text");
    const nextButton = document.getElementById("next-button");

    progressText.textContent = state.progress_text;
    nextButton.classList.add("hidden");

    if (state.completed) {
        speakerLine.textContent = "该场景已经完成，可以回顾记录或重新开始其他场景。";
        hintPanel.classList.add("hidden");
        practiceNote.classList.add("hidden");
        responseInput.disabled = true;
        return;
    }

    responseInput.disabled = false;
    speakerLine.textContent = state.speaker_line || "";
    responseInput.value = "";

    if (state.show_hints) {
        hintPanel.classList.remove("hidden");
        practiceNote.classList.add("hidden");
        taskLabel.textContent = state.task_label || "";
        createListItems(taskBreakdownList, state.task_breakdown || [], (value) => value);
        keywordList.innerHTML = "";
        (state.keywords || []).forEach((keyword) => {
            const chip = document.createElement("span");
            chip.className = "chip";
            chip.textContent = keyword;
            keywordList.appendChild(chip);
        });
        createListItems(frameList, state.sentence_frames || [], (value) => value);
        if (state.can_view_reference && (state.reference_answers || []).length > 0) {
            referenceDetails.classList.remove("hidden");
            referenceDetails.open = false;
            createListItems(referenceList, state.reference_answers || [], (value) => value);
        } else {
            referenceDetails.classList.add("hidden");
            referenceDetails.open = false;
            referenceList.innerHTML = "";
        }
    } else {
        hintPanel.classList.add("hidden");
        practiceNote.classList.remove("hidden");
        if (state.mode === "practice") {
            hintNoteTitle.textContent = "当前为实战模式";
            hintNoteText.textContent = "本轮默认不显示学习提示，请先自行组织回答，再根据反馈调整表达。";
        } else {
            hintNoteTitle.textContent = "学习提示已关闭";
            hintNoteText.textContent = "你已在设置中关闭学习模式提示。本轮请先独立作答，如需提示可到设置页重新开启。";
        }
    }
}

function renderFeedback(result) {
    document.getElementById("feedback-empty").classList.add("hidden");
    document.getElementById("feedback-body").classList.remove("hidden");
    document.getElementById("total-score").textContent = `${result.total_score} / 50`;
    document.getElementById("summary-text").textContent = result.summary;
    document.getElementById("detail-text").textContent = result.detailed_feedback;
    document.getElementById("listener-label").textContent =
        result.recommendation.listener_label || "当前沟通对象";
    document.getElementById("recommended-expression").textContent =
        result.recommendation.recommended_expression || "-";
    document.getElementById("recommendation-note").textContent =
        result.recommendation.style_note || "";

    const scoreGrid = document.getElementById("score-grid");
    const dimensionFeedback = document.getElementById("dimension-feedback");
    const fragmentIssueList = document.getElementById("fragment-issue-list");
    const feedbackReferenceDetails = document.getElementById("feedback-reference-details");
    const feedbackReferenceList = document.getElementById("feedback-reference-list");
    scoreGrid.innerHTML = "";
    dimensionFeedback.innerHTML = "";
    fragmentIssueList.innerHTML = "";
    Object.entries(result.scores || {}).forEach(([label, score]) => {
        const card = document.createElement("div");
        card.className = "score-card";
        card.innerHTML = `<span>${label}</span><strong>${score}</strong>`;
        scoreGrid.appendChild(card);

        const note = document.createElement("div");
        note.className = "dimension-card";
        note.innerHTML = `
            <h4>${label}</h4>
            <p>${(result.dimension_feedback || {})[label] || "本轮暂无该维度解释。"}</p>
        `;
        dimensionFeedback.appendChild(note);
    });

    if ((result.fragment_issues || []).length > 0) {
        (result.fragment_issues || []).forEach((item) => {
            const card = document.createElement("div");
            card.className = "fragment-issue-card";
            card.innerHTML = `
                <p><strong>命中表达：</strong>${item.fragment}</p>
                <p><strong>问题类型：</strong>${item.problem_type}</p>
                <p><strong>修改理由：</strong>${item.reason}</p>
                <p><strong>推荐替换：</strong>${item.replacement}</p>
            `;
            fragmentIssueList.appendChild(card);
        });
    } else {
        const empty = document.createElement("div");
        empty.className = "empty-state";
        empty.textContent = "这一轮没有检测到明显的词语级问题片段。";
        fragmentIssueList.appendChild(empty);
    }

    createListItems(
        document.getElementById("issue-list"),
        result.correction.issues || [],
        (issue) =>
            `<strong>${issue.type}</strong><br><span class="subtle">原表达：</span>${issue.fragment}<br><span class="subtle">原因：</span>${issue.reason}<br><span class="subtle">建议：</span>${issue.replacement}`
    );
    createListItems(
        document.getElementById("suggestion-list"),
        result.correction.suggestions || [],
        (suggestion) =>
            `<strong>原表达：</strong>${suggestion.original}<br><strong>问题类型：</strong>${suggestion.problem_type}<br><strong>修改理由：</strong>${suggestion.reason}<br><strong>推荐替换：</strong>${suggestion.replacement}`
    );
    if (result.mode === "practice" && (result.reference_answers || []).length > 0) {
        feedbackReferenceDetails.classList.remove("hidden");
        feedbackReferenceDetails.open = false;
        createListItems(
            feedbackReferenceList,
            result.reference_answers || [],
            (value) => value
        );
    } else {
        feedbackReferenceDetails.classList.add("hidden");
        feedbackReferenceDetails.open = false;
        feedbackReferenceList.innerHTML = "";
    }

    const note = document.getElementById("status-note");
    if (result.completed && result.completion_summary) {
        note.textContent = `场景完成。累计总分 ${result.completion_summary.total_score}，平均分 ${result.completion_summary.average_score}。`;
    } else if (result.can_continue) {
        note.textContent = "本轮通过，可以进入下一轮。";
    } else if (result.passed === false) {
        note.textContent = "实战模式下本轮未通过，请根据反馈修改后重新提交。";
    } else {
        note.textContent = "";
    }
}

function setupTrainingApp() {
    const app = document.getElementById("training-app");
    if (!app) {
        return;
    }

    const sessionId = app.dataset.sessionId;
    const form = document.getElementById("response-form");
    const responseInput = document.getElementById("response-text");
    const nextButton = document.getElementById("next-button");

    const loadState = async () => {
        const state = await fetchJson(`/api/sessions/${sessionId}/state`);
        renderTurnState(state);
        if (state.completed) {
            responseInput.disabled = true;
            form.querySelector('button[type="submit"]').disabled = true;
        } else {
            form.querySelector('button[type="submit"]').disabled = false;
        }
    };

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const responseText = responseInput.value.trim();
        if (!responseText) {
            return;
        }
        const result = await fetchJson(`/api/sessions/${sessionId}/submit`, {
            method: "POST",
            body: JSON.stringify({ response_text: responseText }),
        });
        renderFeedback(result);
        if (result.can_continue) {
            nextButton.classList.remove("hidden");
        } else {
            nextButton.classList.add("hidden");
        }
        if (result.completed) {
            form.querySelector('button[type="submit"]').disabled = true;
            responseInput.disabled = true;
        }
    });

    nextButton.addEventListener("click", async () => {
        document.getElementById("feedback-body").classList.add("hidden");
        document.getElementById("feedback-empty").classList.remove("hidden");
        document.getElementById("feedback-reference-details").classList.add("hidden");
        await loadState();
    });

    loadState().catch((error) => {
        document.getElementById("speaker-line").textContent = `加载失败：${error.message}`;
    });
}

window.addEventListener("DOMContentLoaded", setupTrainingApp);
