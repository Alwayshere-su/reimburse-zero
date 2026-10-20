from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_DIR = PROJECT_ROOT / "scenarios"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_scenarios() -> List[str]:
    return sorted(path.stem for path in SCENARIO_DIR.glob("*.json"))


def load_scenario(scenario_id: str) -> Dict[str, Any]:
    path = SCENARIO_DIR / f"{scenario_id}.json"
    if not path.exists():
        available = ", ".join(list_scenarios())
        raise ValueError(f"Unknown scenario '{scenario_id}'. Available: {available}")
    return load_json(path)


def compact(value: Any, max_len: int = 180) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


class BaseMockTools:
    """报销稽核场景的 mock 工具基类。

    与官方 Demo 相同的模式:每个 scenario 一个工具实例,所有调用写入 trace,
    供 AgentTeams 通过 HTTP 工具网关主动取证,并沉淀可审计的执行证据。
    """

    def __init__(self, scenario_id: str) -> None:
        self.scenario_id = scenario_id
        self.actions: List[Dict[str, Any]] = []
        self.trace: List[Dict[str, Any]] = []

    def _record(self, tool: str, args: Dict[str, Any], result: Any) -> Any:
        self.trace.append(
            {
                "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "tool": tool,
                "args": args,
                "result_preview": compact(result),
            }
        )
        return result

    def reset(self) -> None:
        self.actions.clear()
        self.trace.clear()

    def get_claim(self) -> Dict[str, Any]:
        raise NotImplementedError

    def list_history_claims(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def verify_invoice(self) -> Dict[str, Any]:
        raise NotImplementedError

    def search_policy(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def execute_payment(self, action: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def rollback_payment(self, action: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def create_approval_task(self, title: str, details: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def resolve_approval(self, task_id: str, decision: str = "approved") -> Dict[str, Any]:
        raise NotImplementedError

    def post_entry(self, action: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def verify_entry(self, claim_id: str) -> Dict[str, Any]:
        raise NotImplementedError


class LocalMockTools(BaseMockTools):
    def __init__(self, scenario_id: str) -> None:
        super().__init__(scenario_id)
        self.scenario = load_scenario(scenario_id)

    def _scenario(self, key: str, default: Any) -> Any:
        return self.scenario.get(key, default)

    def get_claim(self) -> Dict[str, Any]:
        return self._record("mock_claim.get_claim", {}, self.scenario["claim"])

    def list_history_claims(self) -> List[Dict[str, Any]]:
        return self._record("mock_claim.list_history", {}, self._scenario("history_claims", []))

    def verify_invoice(self) -> Dict[str, Any]:
        return self._record("mock_invoice.verify", {}, self.scenario["invoice_verify"])

    def search_policy(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        policies = self._scenario("policies", [])
        if query:
            lowered = query.lower()
            policies = [
                row
                for row in policies
                if lowered in row.get("rule", "").lower()
                or any(lowered in term.lower() for term in row.get("match_terms", []))
            ]
        return self._record("mock_policy.search", {"query": query}, policies)

    def execute_payment(self, action: Dict[str, Any]) -> Dict[str, Any]:
        payment_key = action.get("payment_key")
        # 幂等控制:同一支付键不重复执行
        already = any(
            a.get("action") == "execute_payment" and a.get("payment_key") == payment_key
            for a in self.actions
        )
        if already:
            result = {
                "status": "duplicate",
                "action": "execute_payment",
                "payment_key": payment_key,
                "message": "Idempotent guard: payment already executed for this claim. No duplicate transaction.",
            }
            return self._record("mock_payment.execute", action, result)
        # 合规红线:场景要求审批时,缺少审批回执一律阻断
        approval_required = self.scenario.get("payment_policy", {}).get("approval_required", True)
        if approval_required and not action.get("approval_receipt"):
            result = {
                "status": "blocked",
                "action": "execute_payment",
                "payment_key": payment_key,
                "claim_id": action.get("claim_id"),
                "message": "Payment BLOCKED: approval receipt required. Call mock_approval.create_approval_task and resolve it first. AI never auto-executes fund movement.",
            }
            return self._record("mock_payment.execute", action, result)
        result = {
            "status": "success",
            "action": "execute_payment",
            "payment_key": payment_key,
            "claim_id": action.get("claim_id"),
            "amount": action.get("amount"),
            "account": action.get("account"),
            "approval_receipt": action.get("approval_receipt"),
            "message": "Mock payment executed with idempotency key.",
        }
        self.actions.append(result)
        return self._record("mock_payment.execute", action, result)

    def rollback_payment(self, action: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "status": "success",
            "action": "rollback_payment",
            "payment_key": action.get("payment_key"),
            "message": "Mock payment rollback applied. Ledger and fund flow reverted.",
        }
        self.actions.append(result)
        return self._record("mock_payment.rollback", action, result)

    def create_approval_task(self, title: str, details: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "status": "created",
            "ticket_id": f"APPROVAL-{self.scenario_id.upper()}",
            "title": title,
            "details": details,
            "message": "Approval task created. Payment is BLOCKED until the approval receipt is attached.",
        }
        return self._record("mock_approval.create_approval_task", {"title": title}, result)

    def resolve_approval(self, task_id: str, decision: str = "approved") -> Dict[str, Any]:
        result = {
            "status": "resolved",
            "ticket_id": task_id,
            "decision": decision,
            "approval_receipt": f"RECEIPT-{task_id}",
            "message": "Mock approval resolved. Payment is now permitted only with this approval receipt.",
        }
        self.actions.append(result)
        return self._record("mock_approval.resolve", {"task_id": task_id, "decision": decision}, result)

    def post_entry(self, action: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "status": "success",
            "action": "post_entry",
            "claim_id": action.get("claim_id"),
            "amount": action.get("amount"),
            "account": action.get("account"),
            "message": "Mock ledger entry posted.",
        }
        self.actions.append(result)
        return self._record("mock_ledger.post_entry", action, result)

    def verify_entry(self, claim_id: str) -> Dict[str, Any]:
        posted = any(
            a.get("action") == "post_entry" and a.get("claim_id") == claim_id
            for a in self.actions
        )
        result = {
            "claim_id": claim_id,
            "status": "posted" if posted else "not_posted",
            "message": "Ledger entry verified." if posted else "Ledger entry not found; payment likely blocked.",
        }
        return self._record("mock_ledger.verify_entry", {"claim_id": claim_id}, result)
