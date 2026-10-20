---
name: duplicate-check
description: Detect duplicate reimbursements by matching current claim against historical claims (invoice no, amount, similarity).
metadata:
  version: "0.1.0"
  maturity: demo
---

# 重复报销检测(Duplicate Check)

## Purpose

检测同一发票/费用要素在历史单据中的重复提交(重复报销、一票多报、拆分报销),输出相似命中列表与判定建议。

## Inputs

- 当前单据要素:发票号、金额、报销人、费用日期。
- 历史单据数据(`mock_claim.list_history`)。

## Procedure

1. 精确匹配:发票号完全一致的已支付单据。
2. 相似匹配:同金额/同报销人/时间接近的组合评分。
3. 输出命中列表(相似度 + 历史单据号),给出"疑似重复/正常"建议。

## Output Contract

```json
{
  "hits": [{"claim_id": "", "invoice_no": "", "similarity": 0.0, "status": "paid"}],
  "suggestion": "duplicate|normal|needs_review"
}
```

## Failure Handling

- 历史数据不可用:降级为仅发票号精确匹配;仍缺失则标记"查重未完成",不自动放行。

## Security Boundary

- 历史数据脱敏后入库;仅稽核链路可查;命中结果需稽核 Agent 复核,不作最终结论。

## Reusability

- 可复用于供应商重复付款防重、差旅一票多报、发票台账查重。

## Coordination

- 稽核 Agent 调用;命中结果作为风险信号进入风险评级。
