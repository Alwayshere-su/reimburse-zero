---
name: audit-report
description: Generate structured audit reports from the full evidence chain (claims, decisions, approvals, payments, traces).
metadata:
  version: "0.1.0"
  maturity: demo
---

# 审计报告生成(Audit Report)

## Purpose

按单据/时间/部门维度汇总证据链,生成结构化审计报告:单据清单、稽核结论、异常标注、审批记录、支付回执与证据引用。

## Inputs

- 审计范围(时间区间、部门、单据状态)。
- 证据链数据(执行轨迹、审批事件、支付回执、验真回执、政策引用)。

## Procedure

1. 按审计范围聚合单据与执行证据。
2. 标注异常(超标、疑似重复、伪票、审批驳回)并给出证据引用。
3. 输出结构化审计报告与统计摘要。

## Output Contract

```json
{
  "report_id": "",
  "period": "",
  "claim_count": 0,
  "exceptions": [{"claim_id": "", "type": "", "evidence_refs": []}],
  "approval_records": [],
  "payment_records": [],
  "summary": ""
}
```

## Failure Handling

- 证据缺失:报告标注"证据不完整"并列出缺失项,不掩盖。

## Security Boundary

- 报告只读;仅合规/审计角色可查看;输出脱敏(隐藏报销人敏感信息)。

## Reusability

- 可复用于月度审计、监管报送、供应商风险评估、风控复盘。

## Coordination

- 复盘 Agent 的核心输出;支撑经验沉淀与外部审计。
