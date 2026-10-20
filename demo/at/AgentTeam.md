# Reimburse Zero Demo AgentTeam

这个文件描述 demo 使用的 Team 形态。主运行路径是 AgentTeams + 真实 LLM Worker + HTTP mock 工具网关。

## AgentTeams 运行时

| AgentTeams 概念 | Demo 设计 |
| --- | --- |
| Manager 房间 | 接收自包含的 Agent 创建消息 |
| Team 房间 | Matrix 会话列表中名称以 `Team` 开头;用户通过 `@<team_leader_name>` 发送报销任务 |
| TeamLeader Worker | 创建 Team 时由 manager 生成的独立 Worker `reimburse-zero-demo-leader` |
| Worker 房间 | 运行 5 个角色明确的业务 LLM Agent |
| Worker 运行时 | 统一使用 `qwenpow`(`copow`/`QwenPaw`) |
| 创建策略 | `manager` 串行创建 5 个业务 Worker;创建 Team 时再生成独立 TeamLeader Worker `reimburse-zero-demo-leader`;禁止把业务 Worker 指定为 leader |
| AgentSpec | 5 个业务 Worker 内联在 `at/create_agents_messages.md` |
| 任务输入 | `at/run_demo_task_message.md` 中的报销信息(报销人/费用类型/金额/发票号) |
| 工具调用 | HTTP mock 工具网关 |
| Skill Registry | 当前运行时使用创建消息中的内联 Skill 语义;`skills/*/SKILL.md` 和 `at/nacos_registry_mock.json` 用于评审和后续替换 |

AgentTeams 组件经常运行在 Docker 中,因此运行时不依赖宿主机上的项目目录路径。Worker 通过 HTTP 地址访问工具网关,并根据 `scenario_id` 查询对应报销数据。当前 demo 不要求 Worker 读取宿主机上的 `skills/*/SKILL.md`;后续可把这些 Skill 发布到 Nacos AI Registry 或 AgentTeams Skill Registry,再由 Worker 按版本/标签动态加载。

## 工作流

1. TeamLeader `reimburse-zero-demo-leader` 接收 Team 房间中的报销任务,提取 `claim_id`、`scenario_id` 和用户描述,并调度业务 Worker。
2. `Intake 单据接收 Agent` 解析报销单与发票要素,输出结构化单据候选与初步查重。
3. `稽核 Agent` 主动查询发票验真、政策条款和历史单据,输出合规意见与证据链。
4. `风险评级 Agent` 输出风险等级(L0-L3)与处置建议;打款/可疑单据生成人工审批任务。
5. `处置 Agent` 在审批回执完备前提下执行入账/打款或退回,失败自动回滚。
6. `复盘 Agent` 生成审计报告与规则沉淀建议;TeamLeader 汇总最终报销处置报告。

## Demo 场景

| 场景 | 处置 | 安全策略 |
| --- | --- | --- |
| `normal_claim` | 发票真实、符合差旅标准、无重复 → 低风险自动放行 | L0 自动执行 |
| `excess_claim` | 招待总额超单次上限 → 退回补件,需事前审批说明 | L1 退回补件,不自动放行 |
| `high_risk_claim` | 发票与历史单据高度相似,疑似重复报销 → 生成人工审批任务 | L2 只生成审批计划,打款被阻断 |

## 合规红线

打款等资金动作必须经过人工审批(`mock_approval.create_approval_task`),AI 只输出建议与评级,不自动发起资金支付——这是方案"人机协同审批"的核心,也是评审关注的高风险审批、回滚与审计边界。
