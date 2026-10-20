# AgentTeams 报销任务消息

5 个业务 Worker、独立 TeamLeader Worker `reimburse-zero-demo-leader` 以及 `reimburse-zero-demo` Team 创建完成后,在 Element Web/Matrix 会话列表中找到名称以 `Team` 开头、对应 `reimburse-zero-demo` 的 Team 房间。

进入 Team 房间后,在输入框先输入并选中 `@<team_leader_name>`,再把下面的报销任务复制到这条 @ 消息里发送。不要把任务发给 `manager`。`manager` 用于创建和管理 Agent/Team;Team 房间中的 leader 用于接收业务任务并调度 Worker。

请逐个任务发送:先发送第一笔报销,等 `CLM-2001` 报告完整输出后,再发送第二笔。不要同时发送多笔报销,避免 Team 并发调度时上下文和工具状态互相干扰。

每条消息只包含用户能自然提供的报销信息(报销人、费用类型、金额、发票号、场景 ID)。发票验真、政策条款、历史单据、支付与审批等信息应由 Agent 通过工具网关主动查询。

## 第一次任务:正常差旅报销(低风险,自动放行)

```text
@<team_leader_name>

请让你的 Team 处理一笔新的费用报销。

claim_id: CLM-2001
scenario_id: normal_claim
报销人:王小明(销售部,P6,成本中心 CC-SALES-01)
费用类型:差旅
金额:1860.00 CNY
发票号:CN2026-0001
用途:北京客户拜访差旅费(机票+住宿+市内交通)

请开始稽核与处置,并输出本次报销的完整处置报告。
```

## 第二次任务:超标业务招待(退回补件)

第一笔报告输出完成后,再单独发送下面这条消息。

```text
@<team_leader_name>

请让你的 Team 处理一笔新的费用报销。

claim_id: CLM-2002
scenario_id: excess_claim
报销人:李华(市场部,P7,成本中心 CC-MKT-02)
费用类型:业务招待
金额:6800.00 CNY
发票号:CN2026-0002
用途:重要客户合作洽谈晚宴(8 人)

请开始稽核与处置,并输出本次报销的完整处置报告。
```

## 第三次任务:疑似重复采购报销(高风险,升级人工审批)

第二笔报告输出完成后,再单独发送下面这条消息。

```text
@<team_leader_name>

请让你的 Team 处理一笔新的费用报销。

claim_id: CLM-2003
scenario_id: high_risk_claim
报销人:陈晓(行政部,P5,成本中心 CC-ADMIN-03)
费用类型:采购
金额:15800.00 CNY
发票号:CN2026-0003
用途:笔记本电脑采购(3 台)

请开始稽核与处置,并输出本次报销的完整处置报告。
```
