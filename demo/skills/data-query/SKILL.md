---
name: data-query
description: Query policy and historical claim data, and identify missing evidence to improve decision quality.
metadata:
  version: "0.1.0"
  maturity: demo
---

# 政策与历史数据查询(Data Query)

## Purpose

为稽核与评级链路提供政策数据、历史单据数据查询能力;当证据缺失时,识别并输出数据采集建议,提升后续判定准确率。

## Inputs

- 查询条件(费用类型、职级、时间范围、发票号、报销人)。
- 需要核验的历史单据维度。

## Procedure

1. 按查询条件检索政策条款或历史单据。
2. 对缺失的证据(如历史发票记录、政策版本)输出采集建议。
3. 返回查询结果与数据缺口清单。

## Output Contract

```json
{
  "records": [],
  "data_gaps": ["历史发票记录缺失", "政策版本 v0.2 未发布"],
  "advice": []
}
```

## Failure Handling

- 查询超时或数据源不可用:返回 `data_gaps` 并标记"查询未完成",不伪造数据。

## Security Boundary

- 历史单据数据脱敏后使用;查询权限按角色最小化。

## Reusability

- 可复用于供应商防重付查询、政策版本比对、审计抽样。

## Coordination

- 稽核/评级 Agent 辅助查询;数据缺口回流复盘 Agent 作为采集建议。
