from pathlib import Path
from unittest import TestCase
from typing import List

from parser.report_parser import (
    InlineXBRL,
    extract_inlineXBRL_to_memory,
    parse_inlineXBRL,
    Row,
)


class ReportParserTest(TestCase):
    def test_extract_inlineXBRL_to_memory(self):
        filepath = Path().cwd() / "temp" / "AALI_2022_Audit_rdf.zip"
        files = extract_inlineXBRL_to_memory(filepath, "1410000_1_CurrentYear")
        for file in files:
            self.assertIsInstance(file, InlineXBRL)
            self.assertGreater(file.content.seek(0, 2), 0)

    def test_parse_inlineXBRL(self):
        filepath = Path().cwd() / "temp" / "AALI_2022_Audit_rdf.zip"
        contents = extract_inlineXBRL_to_memory(filepath, "1210000")

        for content in contents:
            rows = parse_inlineXBRL(content)
            self.save_tree_to_file(rows, "tree.txt")

    def save_tree_to_file(self, rows: List[Row], file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            self._write_node(rows, f, indent=0)

    def _write_node(self, rows: List[Row], f, indent=0):
        for row in rows:
            spacing = "  " * indent
            f.write(f"{spacing}L {row.left_header} (Level {row.level})\n")

            if row.children:
                self._write_node(row.children, f, indent + 1)

    def print_tree(self, rows: List[Row], indent=0):
        for row in rows:
            spacing = "  " * indent
            print(f"{spacing}L {row.left_header} (Level {row.level})")
            if row.children:
                self.print_tree(row.children, indent + 1)
