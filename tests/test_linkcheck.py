import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from okf_linkcheck import as_sarif, main, scan


class BundleLinkCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "notes").mkdir()
        (self.root / "tables").mkdir()
        (self.root / "tables" / "orders.md").write_text("---\ntype: Table\n---\n# Orders\n", encoding="utf-8")
        (self.root / "index.md").write_text("[nav](/tables/orders.md)", encoding="utf-8")
        self.doc = self.root / "notes" / "guide.md"

    def test_resolved_missing_unsafe_external_and_code(self):
        self.doc.write_text(
            "---\ntype: Guide\n---\n[ok](/tables/orders.md#schema) [again](../tables/orders.md) "
            "[planned](/tables/future.md) [escape](../../escape.md) "
            "[external](https://example.com/test.md) ![img](/tables/nope.md)\n\n"
            "```md\n[fake](/tables/hidden.md)\n```\n", encoding="utf-8")
        r = scan(self.root)
        self.assertEqual((r["concepts"], r["links_checked"], r["resolved_links"],
                          r["missing_links"], r["unsafe_links"]), (2, 4, 2, 1, 1))
        self.assertEqual(r["edges"], [{"from": "notes/guide", "to": "tables/orders"}])
        self.assertEqual({d["line"] for d in r["diagnostics"]}, {4})
        self.assertEqual(r["diagnostics"][0]["source"], "notes/guide.md")

    def test_reference_links_and_horizontal_rule(self):
        self.doc.write_text("---\ntype: Guide\n---\n[one][o]\n\n---\n\n[two](/tables/orders.md)\n\n[o]: /tables/orders.md\n", encoding="utf-8")
        r = scan(self.root)
        self.assertEqual(r["resolved_links"], 2)
        self.assertEqual(r["missing_links"], 0)

    def test_default_allows_missing_and_opt_in_fails(self):
        self.doc.write_text("[later](/tables/later.md)", encoding="utf-8")
        with redirect_stdout(StringIO()):
            self.assertEqual(main([str(self.root)]), 0)
            self.assertEqual(main([str(self.root), "--fail-on", "missing"]), 1)
            self.assertEqual(main([str(self.root), "--fail-on", "all"]), 1)

    def test_json_and_sarif_are_machine_readable(self):
        self.doc.write_text("[later](/tables/later.md)", encoding="utf-8")
        with redirect_stdout(StringIO()) as output:
            self.assertEqual(main([str(self.root), "--format", "json"]), 0)
        self.assertEqual(json.loads(output.getvalue())["missing_links"], 1)
        result = as_sarif(scan(self.root))
        self.assertEqual(result["version"], "2.1.0")
        self.assertEqual(result["runs"][0]["results"][0]["ruleId"], "missing-target")
        self.assertEqual(result["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["region"]["startLine"], 1)

    def test_output_file_and_no_absolute_bundle_leak(self):
        self.doc.write_text("[ok](/tables/orders.md)", encoding="utf-8")
        p = self.root / "report.json"
        self.assertEqual(main([str(self.root), "--format", "json", "--output", str(p)]), 0)
        report = json.loads(p.read_text())
        self.assertNotIn(str(self.root), p.read_text())
        self.assertEqual(report["edges"], [{"from": "notes/guide", "to": "tables/orders"}])

    def test_missing_root_exit_code(self):
        self.assertEqual(main([str(self.root / "nope")]), 2)

    def test_relative_link_fragment_and_space(self):
        (self.root / "tables" / "order report.md").write_text("# Report", encoding="utf-8")
        self.doc.write_text("[report](../tables/order%20report.md#details)", encoding="utf-8")
        self.assertEqual(scan(self.root)["edges"], [{"from": "notes/guide", "to": "tables/order report"}])

    def test_symlink_target_cannot_escape_bundle(self):
        outside = self.root.parent / "sensitive-do-not-open.md"
        (self.root / "tables" / "out.md").symlink_to(outside)
        self.doc.write_text("[leak](/tables/out.md)", encoding="utf-8")
        self.assertEqual(scan(self.root)["unsafe_links"], 1)

    def test_reserved_indexes_are_not_concepts(self):
        self.doc.write_text("[index](/index.md)", encoding="utf-8")
        r = scan(self.root)
        self.assertEqual(r["links_checked"], 0)
        self.assertEqual(r["missing_links"], 0)


if __name__ == "__main__":
    unittest.main()
