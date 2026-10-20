# MCP Mapping Notes(报销稽核版)

初赛 demo 使用 HTTP mock tool gateway,让 AgentTeams 中的 Docker Worker 可以通过网络访问报销单据、发票验真、报销政策、支付、审批和入账等模拟工具。

当前工具网关不是 MCP Server,但每个 HTTP 工具都有明确的未来 MCP 映射。后续只需要把 HTTP endpoint 替换为真实 MCP Server 或 Higress MCP 代理,Agent 的 Prompt/Skill/工具契约可以保持稳定。

## HTTP 调用协议

```text
POST http://<MOCK_TOOL_BASE_URL>/tools/{scenario_id}/{tool_name}.{function_name}
Content-Type: application/json
```

示例:

```bash
curl -X POST http://127.0.0.1:18089/tools/normal_claim/mock_invoice.verify \
  -H 'Content-Type: application/json' \
  -d '{}'
```

## 工具映射

| HTTP mock tool | Demo function | Future MCP tool | 连接的真实系统 |
| --- | --- | --- | --- |
| `mock_claim` | `get_claim`, `list_history` | `finance.claim_query` | 财务共享系统/ERP 单据查询 |
| `mock_invoice` | `verify` | `tax.invoice_verify` | 税务发票全要素验真接口 |
| `mock_policy` | `search` | `knowledge.policy_rag` | 报销政策知识库(向量 RAG) |
| `mock_payment` | `execute`, `rollback` | `payment.gateway` | 资金/银行支付网关(幂等+回滚) |
| `mock_approval` | `create_approval_task`, `resolve` | `workflow.approval` | 审批流/钉钉企微审批 |
| `mock_ledger` | `post_entry`, `verify_entry` | `finance.ledger` | 财务总账/入账系统 |

## 契约要点(赛题 9.2 等价集成契约)

- **协议**:REST(JSON),工具统一抽象,后续包一层 MCP Server 即可迁移,不改工具调用链;
- **鉴权**:真实接入时 OAuth2 最小权限 + 网关统一身份声明;
- **幂等**:`mock_payment.execute` 支持 `payment_key` 幂等键,重复调用不产生副作用;
- **审批前置**:`mock_approval.create_approval_task` 生成审批任务后,支付必须携带 `approval_receipt` 才能执行——模拟"打款必须人工确认"的合规红线;
- **回滚**:`mock_payment.rollback` 提供失败回滚语义;
- **审计**:每次调用写入 `GET /tools/{scenario_id}/trace`,可导出为执行证据。
