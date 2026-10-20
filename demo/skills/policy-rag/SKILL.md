---
name: policy-rag
description: Retrieve reimbursement policy clauses from the policy knowledge base and return citable evidence for audit decisions.
metadata:
  version: "0.1.0"
  maturity: demo
---

# 报销政策 RAG 比对(Policy RAG)

## Purpose

按员工职级、费用类型、金额与地区检索报销政策条款,返回带出处(政策 ID、版本、条款原文)的判定依据。稽核 Agent 的每个合规判定必须引用政策出处,不依赖模型记忆。

## Inputs

- 员工职级、费用类型、金额、地区、日期。
- 政策知识库(初赛为 mock 检索;复赛替换为向量库 + PolarDB)。

## Procedure

1. 将单据要素转为检索条件(职级/费用类型/金额区间)。
2. 检索政策条款(初赛:mock 关键词检索;复赛:向量语义检索)。
3. 返回命中条款(原文 + 版本 + 匹配度),标注是否有明确限额。
4. 无命中时输出"无明确条款",不臆造政策。

## Output Contract

```json
{
  "hits": [{"policy_id": "", "version": "", "rule": "", "similarity": 0.0}],
  "has_explicit_limit": true,
  "missing_policy": false
}
```

## Failure Handling

- 无命中条款:返回 `missing_policy: true` 并升级人工判断。
- 知识库不可用:降级为精确关键词检索;仍失败则标记"政策核验未完成"。

## Security Boundary

- 政策按版本管理,未发布版本不可检索;检索记录留痕;跨部门政策权限隔离。

## Reusability

- 政策库模板化,任意企业替换政策文档即可复用(差旅/招待/采购/税务合规)。

## Coordination

- 稽核 Agent 的核心判定依据;命中条款同时沉淀为审计证据供复盘 Agent 引用。
