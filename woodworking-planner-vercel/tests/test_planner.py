import json
import io
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request
from unittest import mock
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from planner import CATALOG, TOOLS, PlanError, build_plan  # noqa: E402
from local_server import Handler, get_oci_note  # noqa: E402


def request_data(**overrides):
    data = {
        "idea": "A simple indoor dining table for four",
        "length": 60,
        "width": 32,
        "budget": 250,
        "skill": "beginner",
        "tools": list(TOOLS),
        "inventory": [],
        "confirmed": True,
        "mode": "sample",
    }
    data.update(overrides)
    return data


class PlannerTests(unittest.TestCase):
    def test_all_outputs_reference_one_set_of_parts(self):
        plan = build_plan(request_data())
        ids = {part["id"] for part in plan["parts"]}
        assigned = [part_id for bins in plan["stockAssignment"].values() for stock in bins for part_id in stock["partIds"]]
        self.assertEqual(ids, set(assigned))
        self.assertEqual(len(ids), len(assigned))
        self.assertEqual(ids, set().union(*(set(step["partIds"]) for step in plan["steps"])))
        self.assertEqual(plan["geometry"]["length"], next(part["length"] for part in plan["parts"] if part["id"] == "T1"))
        self.assertEqual(plan["geometry"]["width"], next(part["width"] for part in plan["parts"] if part["id"] == "T1"))

    def test_stock_assignments_fit_including_kerf(self):
        plan = build_plan(request_data(length=72, width=40))
        parts = {part["id"]: part for part in plan["parts"]}
        for sku in ("leg_stock", "apron_stock"):
            for stock in plan["stockAssignment"][sku]:
                used = sum(parts[part_id]["length"] + plan["policy"]["kerf"] for part_id in stock["partIds"])
                self.assertLessEqual(used, CATALOG[sku]["length"])
                self.assertAlmostEqual(CATALOG[sku]["length"] - used, stock["remaining"])

    def test_owned_matching_stock_reduces_only_matching_purchases(self):
        base = build_plan(request_data())
        owned = build_plan(request_data(inventory=[
            {"sku": "leg_stock", "quantity": 1, "length": 96, "width": 3.5, "thickness": 3.5, "confirmed": True},
            {"sku": "apron_stock", "quantity": 1, "length": 95, "width": 3.5, "thickness": 0.75, "confirmed": True},
            {"sku": "top_sheet", "quantity": 1, "length": 96, "width": 48, "thickness": 0.75, "confirmed": False},
        ]))
        self.assertEqual(base["estimate"]["purchaseSubtotal"] - owned["estimate"]["purchaseSubtotal"], CATALOG["leg_stock"]["unitPrice"])
        rows = {item["sku"]: item for item in owned["shopping"]}
        self.assertEqual(rows["leg_stock"]["ownedUsed"], 1)
        self.assertEqual(rows["apron_stock"]["ownedUsed"], 0)
        self.assertEqual(rows["top_sheet"]["ownedUsed"], 0)

    def test_dimensions_regenerate_all_dependents(self):
        small = build_plan(request_data(length=48, width=28))
        large = build_plan(request_data(length=72, width=40))
        self.assertNotEqual(small["revision"], large["revision"])
        self.assertNotEqual(small["geometry"], large["geometry"])
        for part_id in ("A1", "B1", "T1"):
            self.assertNotEqual(next(part["length"] for part in small["parts"] if part["id"] == part_id), next(part["length"] for part in large["parts"] if part["id"] == part_id))
        self.assertIn("61 in", next(step["action"] for step in large["steps"] if step["id"] == "S3"))

    def test_skill_changes_words_not_geometry(self):
        beginner = build_plan(request_data(skill="beginner"))
        intermediate = build_plan(request_data(skill="intermediate"))
        self.assertEqual(beginner["parts"], intermediate["parts"])
        self.assertEqual(beginner["shopping"], intermediate["shopping"])
        self.assertNotEqual(beginner["steps"][0]["detail"], intermediate["steps"][0]["detail"])

    def test_missing_tools_and_invalid_dimensions_block(self):
        with self.assertRaises(PlanError) as missing:
            build_plan(request_data(tools=[key for key in TOOLS if key != "pocket_jig"]))
        self.assertIn("Pocket-hole jig", missing.exception.message)
        with self.assertRaises(PlanError):
            build_plan(request_data(length=74))
        with self.assertRaises(PlanError):
            build_plan(request_data(confirmed=False))

    def test_budget_overrun_and_price_arithmetic(self):
        plan = build_plan(request_data(budget=100))
        self.assertTrue(plan["estimate"]["overBudget"])
        self.assertEqual(plan["estimate"]["purchaseSubtotal"], round(sum(item["cost"] for item in plan["shopping"]), 2))

    def test_oci_boundary_uses_server_key_and_returns_separate_note(self):
        plan = build_plan(request_data())
        fake = io.BytesIO(json.dumps({"choices": [{"message": {"content": "Measure, cut, dry fit, then assemble."}}]}).encode())
        with mock.patch.dict(os.environ, {"OCI_GENAI_API_KEY": "test-secret", "OCI_GENAI_REGION": "us-chicago-1"}):
            with mock.patch("urllib.request.urlopen", return_value=fake) as call:
                note = get_oci_note(plan)
        self.assertEqual(note["source"], "OCI Generative AI")
        self.assertIn("dry fit", note["text"])
        self.assertIn("generativeai.us-chicago-1.oci.oraclecloud.com", call.call_args.args[0].full_url)
        self.assertEqual(call.call_args.args[0].get_header("Authorization"), "Bearer test-secret")
        self.assertNotIn("test-secret", json.dumps(plan))


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        except PermissionError:
            raise unittest.SkipTest("Local socket binding is unavailable in this execution environment") from None
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_demo_request_and_static_page(self):
        with urllib.request.urlopen(self.base + "/") as response:
            self.assertIn(b"Benchline", response.read())
        body = json.dumps(request_data()).encode()
        request = urllib.request.Request(self.base + "/api/plan", data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request) as response:
            plan = json.load(response)
        self.assertEqual(plan["ai"]["source"], "Sample preview")
        self.assertEqual(plan["geometry"]["length"], 60)

    def test_oci_mode_fails_honestly_without_key(self):
        old = os.environ.pop("OCI_GENAI_API_KEY", None)
        try:
            body = json.dumps(request_data(mode="oci")).encode()
            request = urllib.request.Request(self.base + "/api/plan", data=body, headers={"Content-Type": "application/json"})
            with self.assertRaises(urllib.error.HTTPError) as result:
                urllib.request.urlopen(request)
            self.assertEqual(result.exception.code, 502)
            self.assertIn("not configured", json.load(result.exception)["error"])
        finally:
            if old is not None:
                os.environ["OCI_GENAI_API_KEY"] = old


if __name__ == "__main__":
    unittest.main()
