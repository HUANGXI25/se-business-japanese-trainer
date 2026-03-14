# Business Japanese SE Roleplay Trainer

一个本地优先、可解释、可扩展的日本企业 SE 商务日语训练器。

它面向“入社后真实工作沟通”这一非常具体的场景：不是泛泛地练日语会话，而是围绕进度汇报、延期说明、客户确认、风险沟通、协作求助、review 请求等职场对话，做逐轮角色扮演训练。

项目使用 FastAPI + SQLite + Jinja2 + 原生 JavaScript。当前重点是“本地可运行 + 规则反馈可解释 + 场景与规则可扩展”，而不是依赖外部 API 的 AI 对话产品。

## 一眼看懂

- 这是什么：一个面向日本企业 SE 职场场景的逐轮商务日语训练 Web 应用
- 给谁用：新卒 SE、初级工程师、想练真实工作沟通而不是泛会话的学习者
- 为什么不是普通聊天工具：它强调场景推进、规则评分、片段级纠错和可复盘记录，而不是自由聊天

## 这个项目适合谁

这个项目目前最适合以下用户：

- 想练习日本职场商务日语的新卒 SE 或转职初级工程师
- 想围绕真实工作场景做表达训练的日语学习者
- 想扩展规则库、场景库或评分逻辑的开发者
- 想做本地优先语言训练工具原型的开源贡献者

如果你关心的是“如何在日本企业里把话说得更得体、更完整、更像职场沟通”，而不是单纯做语法题，这个项目会更有价值。

## 当前主要功能

- 21 个内置 SE 商务沟通场景，覆盖上司、客户、同事等不同沟通对象
- 学习模式 / 实战模式双模式，分别对应“引导练习”和“独立作答”
- 每轮训练后返回 5 个维度评分、片段级问题指出、修改建议和推荐表达
- 错题本、练习记录、弱点分析，方便后续复盘
- 未来可通过 `llm_interface.py` 接入可选的 LLM 增强能力

## README 截图规划

当前仓库尚未附截图。为了让 GitHub 首页更适合公开展示，建议后续补 3 张图，并按下面的位置插入：

1. 首页总览图
   位置：放在“一眼看懂”之后
   路径：`docs/images/readme/home-overview.png`
   alt text：`首页总览，展示项目定位和入口导航`
2. 训练页反馈图
   位置：放在“当前主要功能”之后
   路径：`docs/images/readme/training-feedback.png`
   alt text：`训练页，展示逐轮输入、评分反馈和推荐表达`
3. 记录与分析图
   位置：放在“数据如何保存”或“如何贡献”之前
   路径：`docs/images/readme/history-and-analytics.png`
   alt text：`练习记录、错题本和弱点分析页面`

截图补齐后，可在 README 中按以下路径插入：

```md
![首页总览，展示项目定位和入口导航](docs/images/readme/home-overview.png)
![训练页，展示逐轮输入、评分反馈和推荐表达](docs/images/readme/training-feedback.png)
![练习记录、错题本和弱点分析页面](docs/images/readme/history-and-analytics.png)
```

## 为什么是“本地优先、可解释、可扩展”

### 本地优先

- 无需外部 API 即可运行
- 练习数据默认保存在本地 SQLite
- 适合个人练习、演示和本地迭代

### 可解释

- 评分依赖明确规则，而不是黑盒判断
- 可以指出命中的词语片段、问题类型和替换建议
- 更适合教学、调试和规则持续改进

### 可扩展

- 场景数据与业务逻辑分离
- 评分、纠错、推荐表达、分析模块拆分清楚
- 已预留 `llm_interface.py`，未来可接入可选增强能力

当前已覆盖的场景包括：

- 向上司汇报进度、延期、风险
- 向客户确认信息、说明变更或影响
- 向同事请求协助、共享问题、请求 review
- 会议沟通、礼貌追问、测试反馈等

## 仓库里现在有什么

- Web 应用入口：`main.py`
- 数据模型与读写：`models.py`、`crud.py`、`database.py`
- 场景和规则：`data/scenarios.json`、`scenario_loader.py`
- 评分和反馈：`scoring_engine.py`、`correction_engine.py`、`recommendation_engine.py`
- 页面与前端：`templates/`、`static/`
- 最小测试与 CI：`tests/`、`.github/workflows/tests.yml`
- 维护文档：`docs/`、`CONTRIBUTING.md`、`SECURITY.md`

## 运行方式

### 1. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动应用

```bash
uvicorn main:app --reload
```

### 4. 打开浏览器

```text
http://127.0.0.1:8000
```

## 页面概览

- `/` 首页
- `/scenarios` 场景列表页
- `/scenarios/{scenario_id}/mode` 模式选择页
- `/train/{session_id}` 对话训练页
- `/mistakes` 错题本
- `/records` 练习记录页
- `/settings` 设置页
- `/analytics` 弱点分析页

## 数据如何保存

练习数据默认保存在本地 SQLite。数据库文件默认位于项目根目录的 `trainer.db`，首次运行时会自动初始化数据库和所需表。

当前数据库主要保存：

- `practice_sessions`
- `practice_turns`
- `mistake_notes`
- `settings`

仓库默认不会提交本地数据库文件、缓存文件或虚拟环境目录。

## 评分与反馈方式

当前版本不依赖外部 AI API，主要使用可解释的规则逻辑：

- 敬语词典匹配
- 商务表达白名单
- 口语表达黑名单
- 场景关键词覆盖率
- 回答长度和完整度判断
- 连接词 / 逻辑结构判断
- 学习模式与实战模式的不同阈值

实战模式下，如果本轮总分、敬语准确度或场景适配度不足，需要重答后才能继续。

## 项目边界与限制

这是一个本地运行的学习型 MVP，不是生产级在线服务。当前边界比较明确：

- 评分是规则驱动，不是真正“理解语义”的智能评估
- 推荐表达和纠错以场景规则为主，覆盖面有限
- 没有用户系统、多用户协作或权限控制
- 默认面向本地运行，不默认考虑公网部署
- 当前已有最小测试和 GitHub Actions，但覆盖面仍然有限

如果你要把它用于公开部署、教学平台或商用产品，还需要额外补充部署、安全和测试工作。

## 如何贡献

最欢迎的贡献方向包括：

- 新增或优化真实 SE 工作场景
- 改进评分解释性和纠错质量
- 提升推荐表达的真实性和对象匹配度
- 修复训练页、记录页、错题本等实际使用问题
- 改进 README 和开发文档
- 补强测试，但优先选择稳定、能防回归的小测试

### 贡献新场景

场景数据位于 `data/scenarios.json`。

建议保持这些原则：

- 场景贴近真实日本企业工作沟通
- 每轮任务目标清晰
- `keywords` 尽量写具体信息块，不只写抽象词
- `sentence_frames` 保持半开放，不直接给完整答案
- `recommended_expression` 只给一条最适合当前对象的表达

### 改进规则

规则主要集中在这些文件：

- `scoring_engine.py`
- `correction_engine.py`
- `recommendation_engine.py`

贡献时请尽量保持：

- 规则可解释
- 输出与场景匹配
- 不夸大项目能力
- 不把外部 API 变成运行前提

更多细节请参考 `CONTRIBUTING.md`。

## 更多文档

- 架构说明：`docs/architecture.md`
- 版本路线图：`docs/roadmap.md`
- 发布前检查：`docs/release-checklist.md`
- 版本记录：`CHANGELOG.md`

## 许可证

本项目使用 MIT License。

之所以选择 MIT，是因为它对个人维护者和早期开源项目都比较友好：

- 简单清晰，便于个人维护
- 允许他人学习、修改和二次开发
- 适合当前这种本地工具型、规则驱动型项目

完整许可证见 `LICENSE`。
