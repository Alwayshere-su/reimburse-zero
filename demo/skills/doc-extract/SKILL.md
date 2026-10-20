---
name: doc-extract
description: Parse reimbursement claims, invoice images, and metadata into a structured claim candidate with data gaps.
metadata:
  version: "0.1.0"
  maturity: demo
---

# 单据解析(Doc Extract)

## Purpose

在 Intake Agent 收到报销单、发票影像与付款申请时,将非结构化输入解析为结构化单据候选(报销人、费用类型、金额、发票要素、附件清单),并标记缺失字段,供后续稽核与查重使用。

## Inputs

- 报销单/付款申请文本与附件清单。
- 发票影像(OCR 文本)或发票要素(发票号、代码、日期、金额、销方、购买方税号)。
- 员工与组织信息(姓名、部门、职级、成本中心)。

## Procedure

1. 提取报销人、部门、职级、成本中心、费用类型、金额、币种、用途与附件列表。
2. 提取发票要素,校验必填字段(发票号/代码/日期/金额/销方/购买方税号)。
3. 汇总缺失字段为 `data_gaps`,不丢弃不完整单据。
4. 输出结构化单据候选,供稽核 Agent 继续核验。

## Output Contract

```json
{
  "claim_id": "CLM-2001",
  "applicant": {"name": "", "dept": "", "level": "", "cost_center": ""},
  "expense": {"type": "差旅", "amount": 0.0, "currency": "CNY", "purpose": ""},
  "invoice": {"invoice_no": "", "issue_date": "", "amount": 0.0, "seller": ""},
  "attachments": [],
  "data_gaps": []
}
```

## Failure Handling

- OCR 置信度低或必填字段缺失:标记为"需人工复核",不进入自动放行。
- 发票要素不完整:保留已提取要素,写入 `data_gaps`,升级人工核验。

## Security Boundary

- 单据数据按最小权限使用,仅稽核链路可见;敏感字段(身份证/银行账号)脱敏后处理。

## Reusability

- 可复用于报销、应付单据、发票台账等任何单据解析场景。

## Coordination

- Intake Agent 使用;输出为稽核 Agent 的输入。
