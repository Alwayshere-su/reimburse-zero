---
name: approval-guard
description: Enforce the approval boundary: payment and high-risk actions are approval-only and never auto-executed.
metadata:
  version: "0.1.0"
  maturity: demo
---

# 审批分级守卫(Approval Guard)

## Purpose

作为资金动作的合规红线守卫:判断动作是否允许自动执行。打款、超限支付、可疑单据(疑似重复/伪票)一律进入人工审批,禁止进入自动执行语义。

## Inputs

- 风险评级 Agent 的评级结果(risk_level/verdict)。
- 动作类型(入账/打款/退回/冲销)与金额。
- 风险策略(risk_policy)。

## Procedure

1. 按动作类型与金额对照风险策略分级。
2. L0/L1 且非资金动作:允许自动执行语义。
3. 打款/冲销/超限/可疑单据:一律创建人工审批任务(`mock_approval.create_approval_task`),输出审批单。
4. 任何情况下不把审批动作放入自动执行列表。

## Output Contract

```json
{
  "action": "",
  "auto_execute_allowed": false,
  "approval_ticket_id": "APPROVAL-...",
  "reason": ""
}
```

## Failure Handling

- 审批流不可用:冻结该动作,标记"等待人工处理",不静默通过。

## Security Boundary

- 审批任务全量留痕(审批人/时间/结论);审批回执是支付执行的强制前置条件。

## Reusability

- 可复用于打款、退款、冲销、权限变更等一切高风险动作的审批边界控制。

## Coordination

- 风险评级 Agent 调用;审批单进入处置 Agent 的支付前置校验。
