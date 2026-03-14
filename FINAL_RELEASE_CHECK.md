# Final Release Check

## 当前判断

基于当前仓库状态，这个项目已经接近“可以公开 GitHub”的标准：

- 本地可运行
- 最小测试可通过
- 基础 OSS 文档已补齐
- README 已能清楚说明项目定位、边界和贡献方式
- 仓库当前索引已不再跟踪本地数据库、缓存和虚拟环境

但在正式公开前，仍建议再确认以下两点：

1. 本轮 README 与截图占位改动是否已整理进一次干净提交
2. 如果仓库尚未公开，是否要处理 git 历史里早期提交过的本地数据库或缓存痕迹

## 公开前最后核对项

### 仓库卫生

- [ ] `git status` 为干净状态
- [ ] `.gitignore` 已覆盖 `.venv/`、`__pycache__/`、`.pytest_cache/`、`.DS_Store`、`trainer.db`
- [ ] 当前没有将本地数据库、缓存或截图草稿误加入提交
- [ ] 当前没有 secrets、token、cookie、密码或私有数据

### 文档

- [ ] `README.md` 已反映当前真实项目状态
- [ ] `CHANGELOG.md` 已包含 `v0.1.0`
- [ ] `MAINTAINER_NOTES.md`、`CONTRIBUTING.md`、`SECURITY.md` 已就位
- [ ] `docs/architecture.md` 和 `docs/roadmap.md` 已就位
- [ ] `docs/release-notes-v0.1.0.md` 已可直接用作 release 草稿

### 运行与测试

- [ ] `pip install -r requirements.txt`
- [ ] `python -m pytest -q`
- [ ] `uvicorn main:app --reload`
- [ ] 首页可访问
- [ ] 至少一条训练链路能正常走通

### 展示层

- [ ] README 首屏能在短时间内说清楚“这是什么、给谁用、为什么不是普通聊天工具”
- [ ] 决定是否现在就补 1 到 3 张真实截图
- [ ] 如果暂时不补截图，README 仍然可独立阅读

## 建议的发布顺序

1. 整理当前未提交改动，确保工作区干净
2. 跑一次本地测试和最小运行验证
3. 决定是否在公开前清理早期 git 历史中的本地数据库/缓存痕迹
4. 确认仓库名、description、topics 和 README 标题
5. 合并发布前最后一个收尾 commit
6. 打 `v0.1.0` tag
7. 创建 GitHub release，并使用 `docs/release-notes-v0.1.0.md` 作为草稿基础
8. 再对外公开仓库或提交 Codex for OSS 申请材料

## tag v0.1.0 前应确认的事项

- [ ] 当前版本确实对应“公开可协作的本地 MVP 基线”
- [ ] 没有仍会让人困惑的临时文件或过渡文档
- [ ] release notes 与 changelog 内容一致
- [ ] README 中的运行方式和测试方式都能实际执行
- [ ] 维护者已接受当前版本仍然是规则驱动 MVP，而不是更成熟产品

## 公开后第一周建议做的维护动作

- 观察首批 issue 是否集中在运行说明、依赖安装或场景理解问题
- 根据外部反馈修正 README、CONTRIBUTING 和截图展示
- 如果有人关注历史卫生问题，再决定是否公开说明或清理 git 历史
- 优先处理会影响首次体验的问题，而不是立刻扩功能
- 记录第一批“适合新贡献者”的 issue，方便后续协作
