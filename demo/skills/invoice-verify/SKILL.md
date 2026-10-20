---
name: invoice-verify
description: Verify invoice authenticity and element consistency against tax invoice verification data.
metadata:
  version: "0.1.0"
  maturity: demo
---

# 发票真伪核验(Invoice Verify)

## Purpose

核验发票真伪与票面要素一致性(发票号/代码/日期/金额/销方/购买方税号),拦截假票与变造票,为稽核判定提供核心证据。

## Inputs

- 发票要素:发票代码、发票号码、开票日期、金额、销方、购买方税号(必要时附影像)。

## Procedure

1. 调用税务验真(`mock_invoice.verify`;复赛替换为真实税局验真 MCP)。
2. 比对返回要素与单据要素的一致性(金额/销方/税号)。
3. 输出验真状态(authentic / forged / unverifiable)与一致性明细。

## Output Contract

```json
{
  "verify_status": "authentic|forged|unverifiable",
  "invoice_no": "",
  "consistency": {"amount": "match|mismatch", "seller": "match|mismatch", "buyer_tax_id": "match|mismatch"},
  "checked_at": ""
}
```

## Failure Handling

- 验真接口超时:重试 3 次(指数退避);仍失败降级为"待人工核验"任务,不阻塞整单流程。
- 状态 unverifiable:不自动放行,升级人工核验。

## Security Boundary

- 仅稽核 Agent 可调用;调用留痕;验真结果只读、不可被 Agent 篡改;发票要素脱敏缓存。

## Reusability

- 可复用于应付发票核验、发票台账管理、供应商发票合规检查。

## Coordination

- 稽核 Agent 调用;验真回执作为合规判定的核心证据,进入审计链。
