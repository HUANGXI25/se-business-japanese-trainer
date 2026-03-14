# Contributing

感谢你关注这个项目。

这个仓库当前是一个本地优先的 Web MVP，重点是让学习者围绕日本企业 SE 场景练习商务日语表达。欢迎务实、可验证、与现有定位一致的贡献。

## 适合贡献的内容

- 新增或改进 SE 商务沟通场景
- 提升评分规则的可解释性
- 改进纠错、推荐表达和弱点分析
- 修复前端交互或页面文案问题
- 改进 README 和使用说明
- 补充最小但有价值的测试

## 本地开发

1. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 启动应用

```bash
uvicorn main:app --reload
```

4. 打开浏览器

```text
http://127.0.0.1:8000
```

应用首次启动时会自动初始化本地 SQLite 数据库。

## 改动前后建议检查

提交前请至少完成以下检查：

```bash
.venv/bin/python -m py_compile main.py database.py crud.py models.py schemas.py scenario_loader.py scoring_engine.py correction_engine.py recommendation_engine.py analytics_engine.py llm_interface.py
.venv/bin/python -c "import main"
.venv/bin/python -m pytest -q
```

如果你的改动影响了训练流程，请至少手动验证：

- 首页可以打开
- 场景列表可以进入
- 训练页可以提交一轮回答
- 记录页和错题本没有明显报错

## 场景与规则贡献建议

### 新增或修改场景

场景数据位于 `data/scenarios.json`。

请尽量保持以下原则：

- 场景贴近真实日本企业 SE 工作沟通
- 每轮目标明确，便于逐轮练习
- 学习提示帮助用户组织表达，而不是直接给完整答案
- `keywords` 优先写具体信息块，不要全部是抽象词
- `recommended_expression` 应与沟通对象匹配，且只给一条最值得学习的表达

### 修改评分或纠错规则

规则逻辑主要在这些文件中：

- `scoring_engine.py`
- `correction_engine.py`
- `recommendation_engine.py`

请尽量保持：

- 规则清晰可解释
- 输出与当前场景匹配
- 不夸大为“真正智能评分”
- 不引入外部 API 作为运行前提

## Issue 建议

提交 issue 时，建议说明：

- 你看到的现象
- 预期行为
- 复现步骤
- 使用的页面或场景
- 相关截图或报错信息

如果问题与某个场景或某轮训练有关，请尽量附上：

- 场景标题或场景 ID
- 模式（学习模式 / 实战模式）
- 你输入的日语回答
- 系统返回的评分或反馈

## Pull Request 建议

提交 PR 时，建议包含：

- 改动目的
- 改动范围
- 手动验证结果
- 如涉及 UI，附 1 到 2 张截图
- 如涉及规则修改，附一个前后对比例子

## 不建议的改动方向

目前不建议直接引入：

- 大规模前端框架替换
- 依赖外部 LLM API 才能运行的核心流程
- 与项目定位无关的泛语言学习功能
- 过度工程化但没有带来实际维护收益的重构
