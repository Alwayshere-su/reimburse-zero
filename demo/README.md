# Reimburse Zero · 企业费用报销智能稽核与处置闭环(AgentTeams 最小 Demo)

> 2026 GOAI【新智基座 | Agent Infra】赛道参赛作品「报销无忧 · 多 Agent 智能稽核与处置闭环」的初赛最小可运行 demo。
> 由官方 OpsPilot Zero Demo 改造而来:复用其 AgentTeams 配置驱动骨架,将运维告警场景替换为**费用报销稽核场景**。

这是一个面向初赛提交的最小可运行 demo。用户只提供报销信息(报销人、费用类型、金额、发票号)和少量初始线索,AgentTeams 中的 5 个业务 LLM Agent 通过 HTTP mock 工具网关主动查询发票验真、报销政策、历史单据、支付与审批数据;创建 Team 时由 manager 创建独立 TeamLeader Worker `reimburse-zero-demo-leader` 负责调度协作,完成"单据接收 → 政策稽核 → 风险评级 → 处置执行 → 复盘沉淀"的零人工干预稽核闭环(资金动作除外,打款必须人工审批)。

完整运行手册见 [at/AGENTTEAMS_RUNBOOK.md](at/AGENTTEAMS_RUNBOOK.md)。

## Demo 要证明什么

1. AgentTeams 可以创建并管理 5 个职责明确的业务 LLM Agent,并在创建 Team 时生成 1 个独立 TeamLeader Worker。
2. Worker 在 Docker 中也能通过 HTTP 工具网关主动取证(验真/政策/查重/支付/审批),不依赖宿主机目录。
3. 三笔模拟报销分三次独立处理,覆盖**自动放行 / 退回补件 / 升级人工审批**三条分支。
4. 低风险动作(L0/L1)进入自动化执行语义;打款等资金动作(L2/L3)**只生成审批计划**,AI 不自动发起支付——合规红线。

## Demo 场景

| 场景 ID | 报销类型 | 预期处置 |
| --- | --- | --- |
| `normal_claim` | 差旅报销 1860 元,发票真实、符合标准、无重复 | 低风险自动放行,入账成功 |
| `excess_claim` | 业务招待 6800 元,总额超单次上限 4000 元 | 退回补件,需事前审批说明 |
| `high_risk_claim` | 采购报销 15800 元,发票与历史单据 CLM-1710 相似度 0.98 | 疑似重复报销,升级人工审批,打款阻断 |

> 全部数据为**模拟脱敏样例**(虚构员工与发票),不包含任何真实企业数据;数据来源与授权边界见方案文档。

## 核心 Agent

| Agent | 作用 | 关键 Skill | 工具 |
| --- | --- | --- | --- |
| Reimburse TeamLeader | 创建 Team 时由 manager 生成的独立 Worker,名称固定为 `reimburse-zero-demo-leader` | 由 manager 创建 | 无直接工具调用 |
| Intake 单据接收 | 解析报销单与发票要素,初步查重 | `doc-extract`, `duplicate-check` | `mock_claim.get_claim`, `mock_claim.list_history` |
| 稽核 Agent | 发票验真、政策 RAG 比对、重复检测、影响评估 | `invoice-verify`, `policy-rag`, `duplicate-check`, `impact-assess` | `mock_invoice.verify`, `mock_policy.search`, `mock_claim.list_history` |
| 风险评级 Agent | 风险分级(L0-L3)与处置建议;打款生成审批任务 | `risk-assess`, `approval-guard` | `mock_policy.search`, `mock_approval.create_approval_task` |
| 处置 Agent | 审批回执前置下执行入账/打款(幂等+回滚)或退回 | `payment-verify`, `approval-guard` | `mock_payment.execute`, `mock_payment.rollback`, `mock_ledger.post_entry`, `mock_ledger.verify_entry` |
| 复盘 Agent | 审计报告、异常模式、规则沉淀建议 | `audit-report`, `data-query` | `mock_ledger.verify_entry`, `mock_policy.search` |

## 最短运行流程

1. 启动 mock 工具网关:

```bash
cd <DEMO_DIR>
python3 tools/mock_tool_server.py --host 0.0.0.0 --port 18089
```

2. 安装 AgentTeams,并按安装器引导在本机完成模型/端口/运行时配置(凭据只保存在本机,不写入仓库;参见 [RUNBOOK 第 3 步](at/AGENTTEAMS_RUNBOOK.md#3-安装-agentteams))。

3. 找到 Docker 容器访问工具网关的地址:

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{println .Gateway}}{{end}}' <manager容器名>
docker exec -it <manager容器名> curl http://<GATEWAY_IP>:18089/health
```

4. 在 Element Web 打开 `manager` 房间,把 [at/create_agents_messages.md](at/create_agents_messages.md) 里的 `<MOCK_TOOL_BASE_URL>` 替换成 `http://<GATEWAY_IP>:18089` 后,将完整创建请求复制给 `manager`。创建请求已要求所有 Worker 使用 `qwenpow`(`copow`/`QwenPaw`)运行时,并由 `manager` 严格串行创建 5 个业务 Worker;创建 Team 时再生成独立 TeamLeader Worker `reimburse-zero-demo-leader`。

5. 在 Element Web/Matrix 会话列表中找到名称以 `Team` 开头、对应 `reimburse-zero-demo` 的 Team 房间。进入房间后,在输入框先 `@<team_leader_name>` 选中带 leader 名字的成员,再把 [at/run_demo_task_message.md](at/run_demo_task_message.md) 中的第一笔报销任务复制到这条 @ 消息里发送;等报告输出完成后,再用同样方式发送第二笔、第三笔。报销任务不要发给 `manager`。

## 合规红线

打款等资金动作必须经过人工审批(`mock_approval.create_approval_task`),AI 只输出建议与评级,不自动发起资金支付。审批任务生成后,支付必须携带审批回执才能执行;支付失败自动回滚。

## 后续替换点

| 当前内容 | 后续替换方向 |
| --- | --- |
| HTTP mock 工具网关 | 真实 MCP Server 或 Higress MCP 代理(税务验真/财务 ERP/支付网关/审批流) |
| `scenarios/*.json` | 真实报销单、发票、政策、历史单据数据源(脱敏) |
| 5 个业务 Worker 的内联 AgentSpec/Skill | Nacos AI Registry 中的 Prompt、Skill、AgentSpec、AgentTeam Spec |
| `skills/*/SKILL.md` 评审材料 | 发布到 Nacos AI Registry 或 AgentTeams Skill Registry,由 Worker 按版本/标签动态加载 |
