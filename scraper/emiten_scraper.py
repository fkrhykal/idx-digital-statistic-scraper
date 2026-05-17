from cloudscraper import CloudScraper
from typing import Literal, TypedDict, List


class Emiten(TypedDict):
    Alamat: str
    BAE: str
    DataID: int
    Divisi: int
    EfekEmiten_EBA: bool
    EfekEmiten_ETF: bool
    EfekEmiten_Obligasi: bool
    EfekEmiten_Saham: bool
    EfekEmiten_SPEI: bool
    Industri: str
    SubIndustri: str
    Email: str
    Fax: str
    id: int
    JenisEmiten: str
    KegiatanUsahaUtama: str
    KodeDivisi: str
    KodeEmiten: str
    NamaEmiten: str
    NPKP: str
    NPWP: str
    PapanPencatatan: str
    Sektor: str
    SubSektor: str
    TanggalPencatatan: str
    Telepon: str
    Website: str
    Status: int
    Logo: str


class Response(TypedDict):
    draw: int
    recordsFiltered: int
    recordsTotal: int
    data: List[Emiten]


def get_emitens(
    emiten_type: Literal["o", "s", "os"] = "s",
    start: int = 0,
    length: int = 10,
    lang: Literal["id", "en"] = "en",
    cloudscrapper: CloudScraper = CloudScraper(),
):
    url = f"https://www.idx.co.id/primary/ListedCompany/GetCompanyProfiles?emitenType={emiten_type}&start={start}&length={length}&lang={lang}"
    response = cloudscrapper.get(url)
    if response.status_code != 200:
        raise Exception(
            f"failed to get {url} status code {response.status_code}", response
        )
    return Response(response.json())
