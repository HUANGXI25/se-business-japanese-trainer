# Architecture

## Overview

Business Japanese SE Roleplay Trainer 是一个本地优先的 FastAPI Web 应用，用于练习日本企业 SE 场景下的逐轮商务日语表达。

当前架构刻意保持简单：

- 后端：FastAPI
- 模板层：Jinja2
- 前端交互：原生 JavaScript
- 数据存储：SQLite
- 场景数据：JSON 文件
- 评分与反馈：本地规则引擎

这个项目当前不是多服务系统，也不依赖外部 API 才能运行。

## High-Level Flow

1. 用户从首页进入场景列表。
2. 选择场景和模式后，创建一个练习 session。
3. 训练页通过 API 获取当前轮次状态。
4. 用户提交日语回答。
5. 后端调用评分、纠错和推荐表达逻辑。
6. 结果写入 SQLite，并返回前端展示。
7. 低分回答可写入错题本，历史回答可用于记录和弱点分析。

## Module Responsibilities

### Application and Routing

- `main.py`
  - FastAPI 应用入口
  - 页面路由与 API 路由
  - 训练 session 状态组装

### Persistence

- `database.py`
  - SQLAlchemy engine 和 session 管理
  - 本地 SQLite 初始化
- `models.py`
  - 数据库模型定义
- `crud.py`
  - 练习记录、错题本、设置等读写逻辑

### Scenario and Rule Engines

- `scenario_loader.py`
  - 读取 `data/scenarios.json`
  - 提供场景、轮次、分类的查询能力
- `scoring_engine.py`
  - 规则评分
  - 维度反馈和片段级问题定位
- `correction_engine.py`
  - 纠错结果生成
- `recommendation_engine.py`
  - 按沟通对象生成单条推荐表达
- `analytics_engine.py`
  - 基于历史记录生成简版弱点分析
- `llm_interface.py`
  - 预留的 LLM 接口适配层
  - 当前仍走本地规则逻辑

### Frontend

- `templates/`
  - 服务端渲染页面
- `static/app.js`
  - 训练页主要交互逻辑
- `static/styles.css`
  - MVP 样式

## Data Model

当前主要使用以下表：

- `practice_sessions`
  - 一次练习会话
- `practice_turns`
  - 每轮回答与得分记录
- `mistake_notes`
  - 低分回答和推荐表达
- `settings`
  - 本地设置项

## Scenario Data Model

场景定义存放在 `data/scenarios.json` 中。每个场景包含：

- 基本信息：`id`、`title`、`description`、`difficulty`、`category`
- 轮次信息：`speaker_line`、`intent`
- 学习提示：`task_breakdown`、`keywords`、`sentence_frames`
- 参考与推荐：`reference_answers`、`recommended_expression`
- 规则辅助字段：`recommended_phrases`、`scoring_keywords`、`listener_type`

这种设计的目标是：

- 便于扩展场景库
- 让提示与评分逻辑保持结构化
- 为后续 LLM 增强保留接口

## Why Local-First, Explainable, Extensible

### Local-First

- 默认本地运行
- 练习数据保存在本地 SQLite
- 不依赖外部模型服务

### Explainable

- 评分来源于明确规则，而不是黑盒判断
- 可以指出命中的词语片段、问题类型和替换建议

### Extensible

- 场景与规则分离
- 模块职责相对清楚
- 已预留 `llm_interface.py`，未来可替换或增强反馈来源

## Current Tradeoffs

当前架构的主要取舍是“可运行、可维护、可扩展优先”，而不是“复杂度最优”或“产品化最完整”。

这意味着：

- 对小项目和公开协作比较友好
- 业务逻辑仍有部分集中在路由层
- 规则引擎能力有限，但可解释性较好
- 当前更适合本地练习工具，而不是大规模在线服务
