# 使用 AgentTeams 运行 Reimburse Zero Demo(报销稽核版)

这份手册面向第一次试运行 demo 的参赛者。运行机器可以是本地 Mac、Linux 服务器或云主机;mock 工具网关和 AgentTeams 都部署在同一台机器上。

核心流程:

1. 启动 HTTP mock 工具网关。
2. 安装 AgentTeams,并按安装器引导完成 LLM 配置。
3. 找到 Docker Worker 可访问的工具网关地址。
4. 在 `manager` 房间创建 5 个业务 Worker,并在创建 Team 时生成独立 TeamLeader Worker。
5. 在 Matrix 会话列表中进入名称以 `Team` 开头的 Team 房间,通过 `@<team_leader_name>` 分别发送三笔报销任务。

## 1. 准备运行机器

需要:

- Docker 或兼容运行时。
- Python 3。
- 一个可用的模型服务凭据(只在本机配置)。

检查:

```bash
python3 --version
docker --version
```

如果没有 Docker,按系统查看官方安装文档(Mac: https://docs.docker.com/desktop/setup/install/mac-install/ ;Ubuntu: https://docs.docker.com/engine/install/ubuntu/ ;其他 Linux: https://docs.docker.com/engine/install/)。安装完成后验证:

```bash
docker run hello-world
```

## 2. 启动 Mock 工具网关

在一个终端中启动服务,并保持它运行:

```bash
cd <DEMO_DIR>
python3 tools/mock_tool_server.py --host 0.0.0.0 --port 18089
```

另开一个终端验证:

```bash
curl http://127.0.0.1:18089/health
curl http://127.0.0.1:18089/scenarios
curl -X POST http://127.0.0.1:18089/tools/normal_claim/mock_invoice.verify \
  -H 'Content-Type: application/json' \
  -d '{}'
```

这一步只验证宿主机本机访问。后面还需要验证 Docker 容器访问。

## 3. 安装 AgentTeams

执行安装脚本(交互安装,按引导在本机完成模型/运行时配置;凭据不要写入仓库):

```bash
bash <(curl -sSL https://higress.ai/hiclaw/install.sh)
```

安装器会引导完成语言、安装模式、版本、LLM、模型凭据、模型联通性测试、Embedding、Manager/Worker 运行时、端口、域名、E2EE、Docker API 安全代理和共享目录等配置。按引导操作即可,关键是看到模型联通性测试通过。

可参考的 demo 样例:

| 引导项 | 样例值 |
| --- | --- |
| 语言 | 中文 |
| LLM | 由安装器在本机配置的模型服务 |
| 模型联通性 | 必须测试通过 |
| Embedding | 可启用;失败后接受自动禁用也可以 |
| Manager/Worker 运行时 | `qwenpow`(`copow`/`QwenPaw`) |
| Element Web 端口 | 默认 `18088` |
| Matrix E2EE | 建议禁用 |
| Docker API 安全代理 | 建议启用 |

安装完成后检查:

```bash
docker ps | grep hiclaw
```

打开 Element Web:

```text
http://127.0.0.1:18088
```

安装配置通常保存到当前用户 HOME 下的 `hiclaw-manager.env`,后续需要调整模型或端口时从这里排查。

## 4. 确定工具网关地址

Worker 在 Docker 容器中运行,不能直接使用 `http://127.0.0.1:18089` 访问宿主机上的 mock 工具网关。单机 Docker 部署优先使用 manager 容器所在网络的 gateway 地址。

```bash
docker ps --format '{{.Names}}' | grep manager
docker inspect -f '{{range .NetworkSettings.Networks}}{{println .Gateway}}{{end}}' <manager容器名>
```

假设输出是 `172.18.0.1`,则 `<MOCK_TOOL_BASE_URL>` 使用:

```text
http://172.18.0.1:18089
```

从容器内验证:

```bash
docker exec -it <manager容器名> curl http://172.18.0.1:18089/health
```

如果这条命令返回 `{"ok": true, ...}`,说明后续 Worker 可以访问工具网关。`host.docker.internal` 只在部分 Docker Desktop 环境可用;如果容器里报 `Could not resolve host`,就使用上面的 gateway 地址。

## 5. 创建 Agent 和 Team

进入 Element Web 的 `manager` 房间。

打开 [create_agents_messages.md](create_agents_messages.md),先把文件中的 `<MOCK_TOOL_BASE_URL>` 全部替换为第 4 步确认的地址,例如:

```text
http://172.18.0.1:18089
```

然后将 [create_agents_messages.md](create_agents_messages.md) 中"复制到 Manager 的完整创建请求"整段发送给 `manager`。这段请求已经包含 5 个业务 Worker 和 1 个 Team 的完整定义,并明确要求:

1. 所有 Worker 使用 `qwenpow`(`copow`/`QwenPaw`)运行时。
2. `manager` 必须逐个创建 Worker,不能并行创建。
3. 必须确认前一个 Worker 创建成功且正常运行后,再创建下一个 Worker。
4. 创建 Team 时必须生成新的独立 Worker `reimburse-zero-demo-leader` 作为 TeamLeader,不能把 5 个业务 Worker 中的任何一个直接指定为 leader。

注意:

- `manager` 只负责创建和管理。
- 报销任务后续发给 Matrix 会话列表中名称以 `Team` 开头的 Team 房间,并在消息里 `@<team_leader_name>`,不发给 `manager`。
- 5 个业务 Worker 的 AgentSpec、Skill 和工具契约已经内联在创建消息中。
- `skills/*/SKILL.md` 主要用于评审、PPT/文档追溯和后续 Registry 替换。

## 6. 发送报销任务

打开 [run_demo_task_message.md](run_demo_task_message.md)。

在 Element Web/Matrix 会话列表中找到名称以 `Team` 开头、对应 `reimburse-zero-demo` 的 Team 房间。通常 `manager` 在创建完成摘要里会告诉你 Team 房间名称和 `team_leader_name`。

进入 Team 房间后,在输入框先输入并选中 leader mention:

```text
@<team_leader_name>
```

然后把第一笔报销任务复制到这条 @ 消息里发送。必须逐个任务发送:等 `CLM-2001` 报告完整输出后,再用同样方式 `@<team_leader_name>` 并发送第二笔、第三笔。不要同时发送多笔报销,避免 Team 并发调度时上下文和工具状态互相干扰。

如果你只看到 `manager` 房间,可以先问:

```text
reimburse-zero-demo 对应的 Team 房间在哪里?请告诉我 Matrix 会话列表中名称以 Team 开头的房间名称,以及需要 @ 的 team_leader_name。
```

任务消息只包含报销信息(报销人、费用类型、金额、发票号)。发票验真、政策条款、历史单据、支付与审批等信息应由 Agent 通过 HTTP 工具网关主动查询。

## 7. 判断是否跑通

`CLM-2001 / normal_claim` 应包含:

| 检查项 | 期望信号 |
| --- | --- |
| 发票验真 | `verify_status=authentic`,要素一致 |
| 政策比对 | 差旅标准命中,住宿未超 500 元/天上限 |
| 查重 | 无重复命中(similarity 低) |
| 风险评级 | L0,自动放行 |
| 处置 | 入账成功;若打款需审批回执 |

`CLM-2002 / excess_claim` 应包含:

| 检查项 | 期望信号 |
| --- | --- |
| 发票验真 | authentic |
| 政策比对 | 招待总额 6800 > 上限 4000,人均 850 > 300 |
| 风险评级 | L1,退回补件(不自动放行) |

`CLM-2003 / high_risk_claim` 应包含:

| 检查项 | 期望信号 |
| --- | --- |
| 发票验真 | authentic(票是真的,但重复使用) |
| 查重 | 与 CLM-1710 相似度 0.98,疑似重复 |
| 风险评级 | L2,生成人工审批任务 |
| 审批 | 打款被阻断,仅生成审批计划;审批通过后才允许支付 |

如果团队要求你人工提供完整发票、政策或历史单据,可以提醒:

```text
请通过已配置的 HTTP mock 工具网关主动查询,不要让我人工收集完整证据。
```

## 8. 收集运行证据(供 PPT)

- Element 聊天记录导出:Agent 决策过程与最终报告,即 Trace 级证据。
- mock 网关工具调用记录:`GET http://127.0.0.1:18089/tools/{scenario_id}/trace`。
- 报告截图:三笔报销的处置报告(自动放行 / 退回补件 / 升级审批)。

## 后续替换点

| 当前内容 | 后续替换方向 |
| --- | --- |
| HTTP mock 工具网关 | 真实 MCP Server 或 Higress MCP 代理(税务验真/财务 ERP/支付网关/审批流) |
| `scenarios/*.json` | 真实报销单、发票、政策、历史单据数据源(脱敏) |
| `at/create_agents_messages.md` 中 5 个业务 Worker 的内联 AgentSpec/Skill | Nacos AI Registry 中的 Prompt、Skill、AgentSpec、AgentTeam Spec |
| `skills/*/SKILL.md` 评审材料 | 发布到 Nacos AI Registry 或 AgentTeams Skill Registry,由 Worker 按版本/标签动态加载 |
