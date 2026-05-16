from pathlib import Path
from unittest import TestCase
from typing import List

from parser.report_parser import (
    InlineXBRL,
    extract_inlineXBRL_to_memory,
    parse_inlineXBRL,
)

from parser.balance_sheet import Row


class ReportParserTest(TestCase):
    def test_extract_inlineXBRL_to_memory(self):
        filepath = Path().cwd() / "temp" / "AALI_2022_Audit_rdf.zip"
        files = extract_inlineXBRL_to_memory(filepath, "1410000_1_CurrentYear")
        for file in files:
            self.assertIsInstance(file, InlineXBRL)
            self.assertGreater(file.content.seek(0, 2), 0)
