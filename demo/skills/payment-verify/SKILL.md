---
name: payment-verify
description: Execute permitted payments idempotently with approval receipts, and verify or roll back on failure.
metadata:
  version: "0.1.0"
  maturity: demo
---

# 支付执行与回滚验证(Payment Verify)

## Purpose

处置 Agent 的唯一资金出口:在审批回执完备前提下执行打款/入账,保证幂等与可回滚,并验证执行结果。

## Inputs

- 处置指令(claim_id、收款账户、金额、payment_key 幂等键)。
- 审批回执(approval_receipt,高风险动作必须携带)。

## Procedure

1. 校验审批回执:缺失或过期则拒绝执行,返回 `approval_required`。
2. 携带 payment_key 调用支付(`mock_payment.execute`),幂等防重。
3. 支付成功后入账(`mock_ledger.post_entry`)并验证(`mock_ledger.verify_entry`)。
4. 失败时调用回滚(`mock_payment.rollback`),记录失败原因。

## Output Contract

```json
{
  "payment_status": "success|duplicate|blocked|failed",
  "payment_key": "",
  "receipt": "",
  "rollback": false,
  "error": ""
}
```

## Failure Handling

- 支付失败:自动回滚 + 记录原因;重试需重新携带审批回执。
- 重复调用:幂等键拦截,不产生重复交易。

## Security Boundary

- 仅处置 Agent 可调;限额分权;支付回执与失败原因全量入库。

## Reusability

- 可复用于应付付款、退款、差旅结算、供应商付款。

## Coordination

- 处置 Agent 使用;回执与失败原因作为证据进入复盘 Agent 的审计报告。
