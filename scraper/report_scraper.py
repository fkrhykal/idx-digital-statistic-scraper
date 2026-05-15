from cloudscraper import CloudScraper
from typing import List, TypedDict, Iterator
from pathlib import Path
import logging


class Attachment(TypedDict):
    Emiten_Code: str
    File_ID: str
    File_Modified: str
    File_Path: str
    File_Size: int
    File_Type: str
    Report_Period: str
    Report_Type: str
    Report_Year: str
    NamaEmiten: str


class Result(TypedDict):
    Attachments: List[Attachment]


class Payload(TypedDict):
    Results: List[Result]


class ReportParams(TypedDict):
    index_from: int
    page_size: int
    year: int
    report_type: str
    emiten_type: str
    periode: str
    kode_emiten: str
    sort_column: str
    sort_order: str


def is_xbrl(attachment: Attachment):
    return attachment["File_Path"].endswith("inlineXBRL.zip")


def get_inlineXBRL_attachments(
    cloudscrapper: CloudScraper,
    index_from=1,
    page_size=12,
    year=2022,
    report_type="rdf",
    emiten_type="s",
    periode="audit",
    kode_emiten="",
    sort_column="KodeEmiten",
    sort_order="asc",
):
    url = f"https://www.idx.co.id/primary/ListedCompany/GetFinancialReport?indexFrom={index_from}&pageSize={page_size}&year={year}&reportType={report_type}&EmitenType={emiten_type}&periode={periode}&kodeEmiten={kode_emiten}&SortColumn={sort_column}&SortOrder={sort_order}"
    response = cloudscrapper.get(url)
    if response.status_code != 200:
        raise Exception(
            f"failed to get {url} status code {response.status_code}", response
        )
    payload = Payload(response.json())
    for result in payload["Results"]:
        for attachment in result["Attachments"]:
            if is_xbrl(attachment):
                yield attachment


class InlineXBRLZipFile:

    def __init__(
        self,
        emiten_code: str,
        report_period: str,
        report_type: str,
        report_year: str,
        content: bytes,
    ):
        self.emiten_code = emiten_code
        self.report_period = report_period
        self.report_type = report_type
        self.report_year = report_year
        self.content = content


def get_inlineXBRL_zip_files(
    cloudscrapper: CloudScraper,
    attachments: Iterator[Attachment],
    logger=logging.getLogger(__name__),
):
    for attachment in attachments:
        url = f'https://www.idx.co.id/{attachment["File_Path"]}'
        response = cloudscrapper.get(url)
        if response.status_code != 200:
            logger.warning(
                f"failed to get {url} with status code {response.status_code}. skipped."
            )
            continue
        file = InlineXBRLZipFile(
            report_period=attachment["Report_Period"],
            report_type=attachment["Report_Type"],
            report_year=attachment["Report_Year"],
            emiten_code=attachment["Emiten_Code"],
            content=response.content,
        )
        yield file


def save_inlineXBRL_zip_files(
    path: str, files: Iterator[InlineXBRLZipFile], logger=logging.getLogger(__name__)
):
    folder_path = Path(path)
    folder_path.mkdir(parents=True, exist_ok=True)
    for file in files:
        filename = f"{file.emiten_code}_{file.report_year}_{file.report_period}_{file.report_type}.zip"
        filepath = Path(folder_path / filename)
        if filepath.exists():
            logger.warning(f"{filepath} already exists. skipped.")
            continue
        with open(filepath.resolve(), "wb") as f:
            f.write(file["Content"])
        logger.info(f"saved {filepath}")
        yield filepath
