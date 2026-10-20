from __future__ import annotations

import unittest

from demo.tools.mock_tools import LocalMockTools, list_scenarios, load_scenario


class MockToolsTest(unittest.TestCase):
    def test_scenarios_are_available(self) -> None:
        self.assertEqual(
            list_scenarios(),
            ["excess_claim", "high_risk_claim", "normal_claim"],
        )

    def test_scenario_files_have_expected_verdicts(self) -> None:
        expected = {
            "normal_claim": "approve",
            "excess_claim": "return_for_supplement",
            "high_risk_claim": "escalate_to_human",
        }
        for scenario_id, verdict in expected.items():
            with self.subTest(scenario_id=scenario_id):
                scenario = load_scenario(scenario_id)
                self.assertEqual(scenario["expected_decision"]["verdict"], verdict)

    def test_invoice_verification_is_recorded(self) -> None:
        tools = LocalMockTools("normal_claim")
        result = tools.verify_invoice()
        self.assertEqual(result["verify_status"], "authentic")
        self.assertEqual(tools.trace[-1]["tool"], "mock_invoice.verify")

    def test_policy_search_filters_by_term(self) -> None:
        tools = LocalMockTools("normal_claim")
        rows = tools.search_policy("差旅")
        self.assertTrue(rows)
        self.assertTrue(all("差旅" in row["rule"] for row in rows))

    def test_high_risk_payment_is_blocked_without_approval(self) -> None:
        tools = LocalMockTools("high_risk_claim")
        result = tools.execute_payment(
            {
                "payment_key": "pay-high-risk-1",
                "claim_id": "CLM-2003",
                "amount": 15800.00,
                "account": "vendor-001",
            }
        )
        self.assertEqual(result["status"], "blocked")
        self.assertIn("approval receipt required", result["message"])

    def test_payment_succeeds_after_approval_and_is_idempotent(self) -> None:
        tools = LocalMockTools("high_risk_claim")
        task = tools.create_approval_task("重复报销复核", {"claim_id": "CLM-2003"})
        resolved = tools.resolve_approval(task["ticket_id"])
        action = {
            "payment_key": "pay-high-risk-2",
            "claim_id": "CLM-2003",
            "amount": 15800.00,
            "account": "vendor-001",
            "approval_receipt": resolved["approval_receipt"],
        }

        first = tools.execute_payment(action)
        second = tools.execute_payment(action)

        self.assertEqual(first["status"], "success")
        self.assertEqual(second["status"], "duplicate")

    def test_normal_claim_payment_is_allowed_without_approval(self) -> None:
        tools = LocalMockTools("normal_claim")
        result = tools.execute_payment(
            {
                "payment_key": "pay-normal-1",
                "claim_id": "CLM-2001",
                "amount": 1860.00,
                "account": "employee-001",
            }
        )
        self.assertEqual(result["status"], "success")

    def test_ledger_verification_reflects_posted_entry(self) -> None:
        tools = LocalMockTools("normal_claim")
        before = tools.verify_entry("CLM-2001")
        tools.post_entry({"claim_id": "CLM-2001", "amount": 1860.00, "account": "employee-001"})
        after = tools.verify_entry("CLM-2001")

        self.assertEqual(before["status"], "not_posted")
        self.assertEqual(after["status"], "posted")


if __name__ == "__main__":
    unittest.main()
