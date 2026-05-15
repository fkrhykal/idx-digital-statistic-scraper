import logging
import re
from pathlib import Path
from typing import IO, List, Literal, Optional
from zipfile import ZipFile
from bs4 import BeautifulSoup, Tag

ROW_HEADER_RIGHT = "rowHeaderRight"
ROW_HEADER_LEFT = "rowHeaderLeft"
VALUE_CELL = "valueCell"

type BalanceSheet = Literal["1210000"]

type Code = Literal[
    "1000000",
    # General company
    BalanceSheet,
    "1410000_1_CurrentYear",
    "1610000",
    "1611100",
    "1617000",
    "1620200",
    "1621000",
    "1640100",
    "1670000",
    "1691100",
    "1693100",
    "1210000",
    "1410000_2_PriorYear",
    "1611000_1_CurrentYear",
    "1616000",
    "1619000",
    "1620300",
    "1630000",
    "1640300",
    "1671000",
    "1692000",
    "1696000",
    "1321000",
    "1510000",
    "1611000_2_PriorYear",
    "1616100",
    "1620100",
    "1620500",
    "1632000",
    "1641000",
    "1691000a",
    "1693000",
]


class InlineXBRL:
    def __init__(self, code: Code, content: IO[bytes]):
        self.code = code
        self.content = content


def extract_inlineXBRL_to_memory(
    filepath: str | Path,
    code: Code,
    logger=logging.getLogger(__name__),
):
    with ZipFile(filepath, "r") as zip:
        for filename in zip.namelist():
            if filename != f"{code}.html":
                logger.warning(f"{filename} does not match with {code}. skipped.")
                continue
            with zip.open(filename) as f:
                yield InlineXBRL(code=code, content=f)


class ValueCell:
    def __init__(
        self,
        context_ref: str,
        decimals: int,
        format: str,
        id: str,
        name: str,
        scale: int,
        unitref: str,
        value: int,
    ):
        self.context_ref = context_ref
        self.decimals = decimals
        self.format = format
        self.id = id
        self.name = name
        self.scale = scale
        self.unitref = unitref
        self.value = value


class Row:
    def __init__(
        self,
        left_header: str | None = None,
        right_header: str | None = None,
        value_cell: List[ValueCell] = [],
        level=0,
    ):
        self.left_header = left_header
        self.right_header = right_header
        self.level = level
        self.value_cells = value_cell
        self.children: List[Row] = []

    @staticmethod
    def from_tr(tr: Tag):
        tds = tr.find_all("td")
        row = Row()
        left_header: Tag | None = None
        for td in tds:
            cls = td.get("class")
            if cls is None:
                continue
            if ROW_HEADER_LEFT in cls:
                row.left_header = td.text
                left_header = td
                continue
            if ROW_HEADER_RIGHT in cls:
                row.right_header = td.text
                continue
            if VALUE_CELL in cls:
                nonfraction = td.find("ix:nonfraction")
                if nonfraction is None:
                    continue
                value_cell = ValueCell(
                    context_ref=nonfraction.attrs.get("contextref"),
                    decimals=nonfraction.attrs.get("decimals"),
                    format=nonfraction.attrs.get("format"),
                    id=nonfraction.attrs.get("id"),
                    name=nonfraction.attrs.get("name"),
                    scale=nonfraction.attrs.get("scale"),
                    unitref=nonfraction.attrs.get("unitref"),
                    value=nonfraction.text,
                )
                row.value_cells.append(value_cell)
                continue
        if row.left_header is None:
            return None
        left_style = left_header.get("style")
        row.level = Row.__define_level(left_style)
        return row

    @staticmethod
    def __define_level(style: str):
        match = re.search(r"padding-left:\s*([\d.]+)\s*em", style)
        if not match:
            return 0

        padding_value = float(match.group(1))

        return int(padding_value / 1.5)


type Parser = dict[Code, callable(IO[bytes]) : List[Row]]


def parse_1210000(content: IO[bytes]):
    s = BeautifulSoup(content, "xml")

    trs = s.find_all("tr")

    root: List[Row] = []
    ancestors: List[Row] = []

    for tr in trs:
        row = Row.from_tr(tr)
        if row is None:
            continue

        current_level = row.level

        if current_level == 0:
            root.append(row)
        else:
            if current_level - 1 < len(ancestors):
                parent = ancestors[current_level - 1]
                parent.children.append(row)
            else:
                root.append(row)

        if current_level < len(ancestors):
            ancestors[current_level] = row
        else:
            ancestors.append(row)

        del ancestors[current_level + 1 :]

    return root


PARSER: Parser = {"1210000": parse_1210000}


def parse_inlineXBRL(inlineXBRL: InlineXBRL) -> List[Row]:
    return PARSER[inlineXBRL.code](inlineXBRL.content)

    #    <tr>
    #     <td class="titleLeft" colspan="2">Laporan posisi keuangan </td>
    #     <td class="titleRight" colspan="2" style="text-align:right;">Statement of financial position </td>
    #    </tr>
    #    <tr>
    #     <td></td>
    #     <td class="colHeader01" style="width:20%;"> <span>31 December 2022</span> </td>
    #     <td class="colHeader01" style="width:20%;"> <span>31 December 2021</span> </td>
    #    </tr>
    #    <tr>
    #     <td class="rowHeaderLeft" style="width:30%;;font-weight:bold;font-weight:bold;">Aset </td>
    #     <td class="valueCell" style="text-align:right;;background-color:#b8b8b8;vertical-align:middle"></td>
    #     <td class="valueCell" style="text-align:right;;background-color:#b8b8b8;vertical-align:middle"></td>
    #     <td class="rowHeaderRight" style="width:30%;;font-weight:bold;font-weight:bold;">Assets </td>
    #    </tr>

    #    <td class="rowHeaderLeft" style="width:30%;;font-weight:bold;font-weight:bold;">Aset </td>
    #     <td class="valueCell" style="text-align:right;;background-color:#b8b8b8;vertical-align:middle"></td>
    #     <td class="valueCell" style="text-align:right;;background-color:#b8b8b8;vertical-align:middle"></td>
    #     <td class="rowHeaderRight" style="width:30%;;font-weight:bold;font-weight:bold;">Assets </td>

    #    <tr>
    #     <td class="rowHeaderLeft" style="width:30%;;padding-left:1.5em;font-weight:bold;font-weight:bold;">Aset lancar </td>
    #     <td class="valueCell" style="text-align:right;;background-color:#b8b8b8;vertical-align:middle"></td>
    #     <td class="valueCell" style="text-align:right;;background-color:#b8b8b8;vertical-align:middle"></td>
    #     <td class="rowHeaderRight fixedFormRowHeaderRight" style="width:30%;;padding-right:1.5em;text-align: right;border-bottom:1px solid #CCCCCC;;font-weight:bold;font-weight:bold;">Current assets </td>
    #    </tr>
    #    <tr>

    #   <tr>
    #     <td class="rowHeaderLeft" style="width:30%;;padding-left:3.0em">Kas dan setara kas</td>
    #     <td class="valueCell" style="text-align:right;;vertical-align:middle">
    #      <ix:nonfraction contextref="CurrentYearInstant" decimals="-6" format="ixt:numcommadot" id="IX02_0036_00001_01_0001" name="idx-cor:CashAndCashEquivalents" scale="6" unitref="IDR">
    #        1,619,616
    #      </ix:nonfraction> </td>
    #     <td class="valueCell" style="text-align:right;;vertical-align:middle">
    #      <ix:nonfraction contextref="PriorEndYearInstant" decimals="-6" format="ixt:numcommadot" id="IX02_0036_00003_01_0001" name="idx-cor:CashAndCashEquivalents" scale="6" unitref="IDR">
    #        3,896,022
    #      </ix:nonfraction> </td>
    #     <td class="rowHeaderRight fixedFormRowHeaderRight" style="width:30%;;padding-right:3.0em;text-align: right;border-bottom:1px solid #CCCCCC;">Cash and cash equivalents</td>
    #    </tr>
