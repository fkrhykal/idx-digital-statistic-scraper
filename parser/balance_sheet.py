import re

from bs4 import BeautifulSoup, Tag
from typing import IO, List


class Left:
    def __init__(self, style: str, label: str):
        self.style = style
        self.label = label

    @staticmethod
    def _is_left(td: Tag):
        return td.get("class") is not None and "rowHeaderLeft" in td.get("class")

    @staticmethod
    def from_tag(td: Tag):
        if Left._is_left(td):
            return Right(td.get("style"), td.text)
        return None


class Right:
    def __init__(self, style: str, label: str):
        self.style = style
        self.label = label

    @staticmethod
    def _is_right(td: Tag):
        return td.get("class") is not None and "rowHeaderRight" in td.get("class")

    @staticmethod
    def from_tag(td: Tag):
        if Right._is_right(td):
            return Right(td.get("style"), td.text)
        return None


class Header:
    def __init__(self, left: Left, right: Right):
        self.left = left
        self.right = right


class ValueCell:
    def __init__(
        self,
        ix: str,
        context_ref: str,
        decimals: int,
        format: str,
        id: str,
        name: str,
        scale: int,
        unitref: str,
        value: int,
    ):
        self.ix = ix
        self.context_ref = context_ref
        self.decimals = decimals
        self.format = format
        self.id = id
        self.name = name
        self.scale = scale
        self.unitref = unitref
        self.value = value

    # TODO: perlu direfactor nanti, setidaknya kalau ketemu value cell selain nonfraction.
    @staticmethod
    def _get_value_kind(td: Tag):
        ix = td.find("ix:nonfraction")
        if ix is None:
            return None
        return ix

    # TODO: perlu direfactor nanti, setidaknya kalau ketemu value cell selain nonfraction.
    @staticmethod
    def from_tag(td: Tag):
        ix = ValueCell._get_value_kind(td)
        if ix is None:
            return None
        return ValueCell(
            ix="ix:nonfraction",
            context_ref=ix.attrs.get("contextref"),
            decimals=ix.attrs.get("decimals"),
            format=ix.attrs.get("format"),
            id=ix.attrs.get("id"),
            name=ix.attrs.get("name"),
            scale=ix.attrs.get("scale"),
            unitref=ix.attrs.get("unitref"),
            value=ix.text,
        )


class Row:
    def __init__(
        self,
        header: Header,
        value_cells: List[ValueCell] = [],
    ):
        self.header = header
        self.value_cells = value_cells
        self.children: List[Row] = []
        self.level = Row._define_level(header)

    @staticmethod
    def from_tr(tr: Tag):
        tds = tr.find_all("td")
        left_header = None
        right_header = None
        value_cells = []
        header = None
        for td in tds:
            right = Right.from_tag(td)
            if right is not None:
                right_header = right
                continue
            left = Left.from_tag(td)
            if left is not None:
                left_header = left
                continue
            value_cell = ValueCell.from_tag(td)
            if value_cell is not None:
                value_cells.append(value_cell)

        if left_header is None:
            return None

        header = Header(left_header, right_header)

        return Row(
            header=header,
            value_cells=value_cells,
        )

    @staticmethod
    def _define_level(header: Header):
        match = re.search(r"padding-left:\s*([\d.]+)\s*em", header.left.style)
        if not match:
            return 0
        padding_value = float(match.group(1))
        return int(padding_value / 1.5)


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
