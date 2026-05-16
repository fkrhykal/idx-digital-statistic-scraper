from pathlib import Path
from typing import IO, List, Literal
from zipfile import ZipFile
from parser.balance_sheet import parse_1210000, Row

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
):
    with ZipFile(filepath, "r") as zip:
        for filename in zip.namelist():
            if filename != f"{code}.html":
                continue
            with zip.open(filename) as f:
                yield InlineXBRL(code=code, content=f)


PARSER = {"1210000": parse_1210000}


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
