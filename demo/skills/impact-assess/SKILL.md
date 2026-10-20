---
name: impact-assess
description: Assess the financial impact of a claim against policy limits, budget, and risk exposure.
metadata:
  version: "0.1.0"
  maturity: demo
---

# 金额与影响评估(Impact Assess)

## Purpose

评估一笔报销/应付单据的金额影响:是否超政策限额、超预算、涉及高风险科目,并给出影响等级,供风险评级 Agent 决策。

## Inputs

- 结构化单据候选(费用类型、金额、职级、成本中心)。
- 政策条款命中结果。
- 预算/成本中心信息(如有)。

## Procedure

1. 将单据金额与命中政策的限额(人均/单次/每日)对比,计算超限金额与比例。
2. 判断是否涉及高风险科目(采购、招待、大额现金)或需要事前审批的额度。
3. 输出影响等级(低/中/高)与超限明细。

## Output Contract

```json
{
  "impact_level": "low|medium|high",
  "limit_hits": [{"policy_id": "", "limit": 0, "actual": 0, "exceed": 0}],
  "risk_subjects": [],
  "needs_preapproval": false
}
```

## Failure Handling

- 政策未命中或无明确限额:影响等级保守评估为 medium,升级人工判断,不臆造限额。

## Security Boundary

- 预算与薪酬类数据仅对稽核/评级链路可见,输出不含员工敏感信息。

## Reusability

- 可复用于预算管控、成本中心费用分析、供应商应付评估。

## Coordination

- 稽核 Agent 调用,输出供风险评级 Agent 使用。
