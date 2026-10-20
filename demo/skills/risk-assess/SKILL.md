---
name: risk-assess
description: Rate claim risk and produce disposition (approve / return / escalate) with evidence-backed reasoning.
metadata:
  version: "0.1.0"
  maturity: demo
---

# 风险评级与处置建议(Risk Assess)

## Purpose

综合发票验真结果、政策比对结论、重复报销检测与金额影响评估,输出风险等级(L0-L3)与处置建议(自动放行/退回补件/升级人工审批),并说明理由。

## Inputs

- 稽核 Agent 结论(验真结果、政策命中、查重命中)。
- 金额影响评估结果。
- 风险策略(来自 team_spec 的 risk_policy)。

## Procedure

1. 聚合验真、政策、查重、影响四类信号。
2. 按风险矩阵定级:L0 完全合规 / L1 需补件或轻微超标 / L2 疑似重复或超审批线 / L3 涉及资金高风险或明确违规。
3. 对照 risk_policy 输出处置:自动执行仅限 L0/L1;L2/L3 只生成审批计划。
4. 每次评级附证据引用与理由。

## Output Contract

```json
{
  "risk_level": "L0|L1|L2|L3",
  "verdict": "approve|return_for_supplement|escalate_to_human|reject",
  "reason": "",
  "evidence_refs": [],
  "approval_required": false
}
```

## Failure Handling

- 信号冲突(如验真通过但查重命中):以最高风险信号为准,升级人工判断。
- 关键证据缺失:保守评级,不自动放行。

## Security Boundary

- 评级仅作建议,不构成最终资金决策;打款类动作必须由人工审批。

## Reusability

- 可复用于供应商付款、退款、报销等多类资金动作的风险分级。

## Coordination

- 风险评级 Agent 使用;处置建议交给处置 Agent,审批要求交给审批链路。
