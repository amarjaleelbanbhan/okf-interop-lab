import tempfile
import unittest
from pathlib import Path

from interop import edges, probe, resolve


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "tables").mkdir()
        (self.root / "notes").mkdir()
        (self.root / "tables" / "orders.md").write_text("---\ntype: Table\n---\nOrders")
        self.source = self.root / "notes" / "a.md"

    def test_both_forms_fragment_encoded_duplicate_and_missing(self):
        self.source.write_text('---\ntype: Note\n---\n[A](/tables/orders.md#schema) '
                               '[B](../tables/orders.md) [C](/tables/orders.md) '
                               '[broken](/tables/absent.md)')
        self.assertEqual(edges(self.root, self.source), ["tables/orders"])

    def test_escape_external_and_symlink(self):
        outside = self.root.parent / "outside.md"
        (self.root / "notes" / "link.md").symlink_to(outside)
        for href in ("../../outside.md", "https://example.org/a.md", "//host/a.md",
                     "file:///tmp/a.md", "link.md", "..%2f..%2foutside.md",
                     "\\\\host\\file.md"):
            self.assertIsNone(resolve(self.root, self.source, href), href)

    def test_reserved_and_empty(self):
        (self.root / "index.md").write_text("index")
        self.assertIsNone(resolve(self.root, self.source, "/index.md"))
        self.assertEqual(probe(self.root)["results"],
                         [{"source": "tables/orders.md", "resolved": []}])


if __name__ == "__main__":
    unittest.main()


class MarkdownParsingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "notes").mkdir()
        (self.root / "tables").mkdir()
        (self.root / "tables" / "orders.md").write_text("# Orders")
        (self.root / "tables" / "other.md").write_text("# Other")
        self.source = self.root / "notes" / "note.md"

    def test_ignore_fenced_and_inline_code(self):
        self.source.write_text(
            "---\ntype: Note\n---\n"
            "```md\n[fake](/tables/other.md)\n```\n"
            "`[inline](/tables/other.md)`\n"
            "[real](/tables/orders.md)\n"
        )
        self.assertEqual(edges(self.root, self.source), ["tables/orders"])

    def test_horizontal_rule_does_not_discard_earlier_links(self):
        self.source.write_text(
            "---\ntype: Note\n---\n"
            "[before](/tables/orders.md)\n\n---\n\n[after](/tables/other.md)\n"
        )
        self.assertEqual(edges(self.root, self.source), ["tables/orders", "tables/other"])

    def test_reference_links_and_image_exclusion(self):
        self.source.write_text(
            "[real][orders] ![picture](/tables/other.md)\n\n"
            "[orders]: /tables/orders.md#details\n"
        )
        self.assertEqual(edges(self.root, self.source), ["tables/orders"])

    def test_encoded_space_and_encoded_backslash(self):
        (self.root / "tables" / "order report.md").write_text("# Report")
        self.assertEqual(resolve(self.root, self.source, "/tables/order%20report.md"),
                         "tables/order report")
        self.assertIsNone(resolve(self.root, self.source, "..%5C..%5Coutside.md"))

    def test_resolve_rejects_source_outside_bundle(self):
        outside = self.root.parent / "unrelated-source.md"
        self.assertIsNone(resolve(self.root, outside, "/tables/orders.md"))

    def test_no_frontmatter_horizontal_rule_at_start(self):
        self.source.write_text("---\n[real](/tables/orders.md)\n")
        self.assertEqual(edges(self.root, self.source), ["tables/orders"])
