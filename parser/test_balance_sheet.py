from unittest import TestCase
from pathlib import Path
from parser.report_parser import extract_inlineXBRL_to_memory
from parser.balance_sheet import parse_1210000, Row
from typing import List


class TestBalanceSheet(TestCase):

    def test_parse_1210000(self):
        filepath = Path().cwd() / "temp" / "AALI_2022_Audit_rdf.zip"
        contents = extract_inlineXBRL_to_memory(filepath, "1210000")

        for content in contents:
            rows = parse_1210000(content.content)
            self.save_tree_to_file(rows, "tree.txt")

    def save_tree_to_file(self, rows: List[Row], file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            self._write_node(rows, f, indent=0)

    def _write_node(self, rows: List[Row], f, indent=0):
        for row in rows:
            print(row)
            spacing = "  " * indent
            value = row.value_cells[0].value if len(row.value_cells) > 0 else None
            f.write(
                f"{spacing}L {row.header.left.label} (Value {value}) (Level {row.level})\n"
            )

            if row.children:
                self._write_node(row.children, f, indent + 1)

    def print_tree(self, rows: List[Row], indent=0):
        for row in rows:
            spacing = "  " * indent
            print(f"{spacing}L {row.left_header.label} (Level {row.level})")
            if row.children:
                self.print_tree(row.children, indent + 1)
