# Codex Loop Engineering

[English](README.md) | [简体中文](README.zh-CN.md)

Codex Loop Engineering 是一个面向 Codex 的插件，用来把大型、长期、容易反复的任务组织成可控的循环：先明确目标，再拆角色和线程，执行后留下产物、审阅、仲裁和修复记录。

它适合深度重构、大型功能开发、架构变更、研究整理、产品/设计工作流、多文件迁移，或者任何需要长期状态、独立审阅、干净上下文和明确停止条件的任务。

这个项目不是要替代 Superpowers。Superpowers 更像完整开发方法论工具箱；Codex Loop Engineering 更聚焦在 Codex 里的循环编排：用最小但足够的流程控制风险，让任务有目标、有状态、有记录、有反馈，也有停止点。

## 为什么需要它

长任务里，单纯反复提示 Agent 很容易失控：

- 没有完成标准，Agent 不知道什么时候停；
- 没有捕获步骤，下一轮会忘记上一轮发生了什么；
- 没有反馈路径，失败不会改变下一轮输入；
- 没有持久状态，每一轮都像重新开始；
- 没有停止条件，成本、风险和范围会越滚越大。

Codex Loop Engineering 把这些问题拆成六个接口：`goal`、`state`、`context`、`act`、`capture`、`stop`。

## 核心能力

- **Codex 优先的循环框架**：默认由 Codex 负责执行、仲裁和最终验证，Claude 只作为可选规划或只读审阅。
- **不是提示词堆叠，而是生命周期控制**：每个循环都要定义目标、状态、上下文、行动权限、捕获内容和停止规则。
- **可配置角色拓扑**：插件提供编排框架，但 Agent 名称、数量、并行方式和任务拆分都按项目决定。
- **经理/调度式线程管理**：manager 和 dispatcher 负责身份表、工作日志、产物路径、截止时间和交接规则，避免变成混乱群聊。
- **干净上下文边界**：规划、执行、审阅、仲裁等线程只读取自己需要的材料，减少互相污染。
- **单线交接**：线程之间优先通过产物和明确 handoff 通信，而不是互相读完整聊天记录。
- **用户检查点**：遇到产品、范围、取舍或不确定点时停下来问用户，不让循环无限自转。
- **产物优先**：任务简报、合并计划、执行报告、审阅、仲裁和最终报告都作为可追踪产物留下。

## 角色拓扑

Loop Engineering 的重点不是固定一套“经理 Agent / 执行 Agent”的名称，而是给每个任务先设计适合它的角色图。

常见拓扑包括：

- **经理-执行者**：一个经理线程协调多个执行线程和审阅线程。
- **扇出/扇入**：先并行做研究、材料、实现或验证，再回到一个整合线程。
- **线性流水线**：研究、草拟、执行、审阅、发布。
- **审阅循环**：先执行，再用干净上下文审阅，最后由仲裁线程决定修复。
- **混合并行**：视频、内容、数据、设计等不同子任务并行推进，最后统一整合。

每次新任务开始时，都应该先根据任务目标拆出项目专属角色，再生成对应的身份表和工作日志汇总。任务变了，角色图和日志表也应该跟着调整。

## 快速开始

让 Codex 使用这个插件：

```text
Use Codex Loop Engineering for this refactor.
```

启动第一个线程之前，插件应该先问清楚：

- 我们要达成什么结果？什么算“足够好”？
- 需要哪些 Agent/角色？这些名称是否按项目自定义？
- 哪些任务可以并行？哪些必须串行？
- 线程之间怎么通信：只通过 manager、允许直接交接、只读审阅，还是混合？
- 是否需要 Claude 参与规划或只读审阅？
- 哪些节点必须让用户介入确认，而不是自动继续？

如果这些问题还没回答，插件应该暂停，而不是擅自创建固定角色布局。

## 基本工作流

1. **路线选择**：先判断是 T0 直接处理、T1 清单、T2 mini-loop，还是 T3/T4 多线程循环。
2. **角色与身份表**：按任务目标拆 Agent，定义每个角色的权限、产物、通信方式和日志字段。
3. **循环契约**：明确 goal、state、context、act、capture、stop。
4. **规划**：大型或高风险任务可使用 Codex/Claude 独立规划，再合并成唯一执行计划。
5. **执行**：Codex 只按合并计划执行，并留下执行报告。
6. **审阅**：需要时用 Claude 只读审阅和 Codex 独立审阅。
7. **仲裁与修复**：按证据接受、拒绝或延后审阅意见，修复后再验证。
8. **最终报告**：列出变更、验证输出、剩余风险和下一步。

典型产物目录：

```text
docs/loop-engineering/YYYY-MM-DD-slug/
  00-brief.md
  10-plan-claude.md
  11-plan-codex.md
  12-plan-merged.md
  20-execution-report.md
  30-review-claude.md
  31-review-codex-subagent.md
  40-arbitration.md
  50-final-report.md
```

## 安装

这个仓库按 Codex marketplace source 组织。可安装插件位于 `plugins/codex-loop-engineering`。

注册 marketplace source：

```bash
codex plugin marketplace add https://github.com/liujiazhi-arch/codex-loop-engineering
```

安装插件：

```bash
codex plugin add codex-loop-engineering@codex-loop-engineering
```

如果你的 Codex 环境暂时不支持 marketplace install，可以克隆仓库后使用 `plugins/codex-loop-engineering` 下的插件包。

## 什么时候不要用

不要把完整循环用于每一个小任务。它会消耗更多 token，也会增加协调成本。

下面这些情况通常直接让 Codex 做即可：

- 很小的本地修复；
- 简单配置或文档修改；
- 单文件补丁，验证方式很明确；
- 只读解释或问答；
- 一个清单就能管住的小任务。

当丢失状态、上下文混乱、缺少审阅或没有停止规则的成本高于编排开销时，再使用 Codex Loop Engineering。

## 隐私

这个插件不包含 API key、私有 endpoint 或第三方中转代码。它只是工作流插件。你在项目中生成的 brief、plan、review、report 可能包含私有项目信息，公开分享前需要检查。

## 更新

GitHub 仓库更新后，本地已安装插件不会自动同步。

推送新 commit 后，需要运行：

```bash
codex plugin marketplace upgrade codex-loop-engineering
codex plugin add codex-loop-engineering@codex-loop-engineering
```

然后开启新线程，让 Codex 加载更新后的插件包和技能。

## 社区

- Issues: https://github.com/liujiazhi-arch/codex-loop-engineering/issues
- Repository: https://github.com/liujiazhi-arch/codex-loop-engineering

## 许可证

MIT. See [LICENSE](LICENSE).
