# Scraper Statistik Digital IDX

## Deskripsi Proyek

Proyek ini adalah sebuah *scraper* Python yang dirancang untuk mengunduh laporan keuangan dalam format `inlineXBRL.zip` dari situs web Bursa Efek Indonesia (IDX). Laporan-laporan ini, yang diterbitkan oleh perusahaan tercatat, seringkali digunakan untuk analisis data, penelitian, dan statistik. Skrip ini dikembangkan untuk mampu mengatasi perlindungan Cloudflare yang digunakan oleh situs IDX untuk memastikan akses ke data laporan yang relevan.

Tujuan utama dari proyek ini adalah untuk menyediakan alat yang efisien untuk mengumpulkan data laporan keuangan historis atau terkini dari IDX secara terprogram.

## Fitur

*   **Pengunduhan Laporan inlineXBRL:** Mengunduh file `.zip` yang berisi laporan keuangan dalam format `inlineXBRL` langsung dari IDX.
*   **Cloudflare Bypass:** Menggunakan pustaka `cloudscraper` untuk melewati perlindungan anti-bot Cloudflare.
*   **Filter Laporan Fleksibel:** Memungkinkan filter laporan berdasarkan parameter seperti tahun, tipe laporan (misalnya, `rdf` untuk tahunan, `fs` untuk keuangan), periode (misalnya, `audit` untuk audit, `q1`, `q2`, `q3` untuk kuartalan), dan kode emiten spesifik.
*   **Penyimpanan File Terstruktur:** Menyimpan file ZIP yang diunduh ke direktori lokal dengan nama file yang terstruktur (`KodeEmiten_Tahun_Periode_TipeLaporan.zip`) untuk memudahkan pengelolaan dan analisis.
*   **Logging:** Menyediakan logging informatif untuk melacak proses pengunduhan dan penanganan kesalahan.

## Persyaratan

Untuk menjalankan proyek ini, Anda memerlukan:

*   Python 3.7+
*   Pustaka `cloudscraper`

## Instalasi

Ikuti langkah-langkah di bawah ini untuk menginstal dan menyiapkan proyek:

1.  **Kloning Repositori:**
    ```bash
    git clone https://github.com/yourusername/idx-digital-statistic-scrapper.git # Ganti dengan URL repositori Anda
    cd idx-digital-statistic-scrapper
    ```

2.  **Instal Dependensi:**
    Gunakan `pip` untuk menginstal pustaka `cloudscraper`:
    ```bash
    pip install cloudscraper
    ```

## Penggunaan

Modul `scraper/report_scraper.py` berisi semua fungsi inti untuk mengambil dan menyimpan laporan. Anda dapat mengintegrasikannya ke dalam skrip Python Anda sendiri atau membuat *entry point* di `main.py` untuk menjalankan proses *scraping*.

Berikut adalah contoh bagaimana Anda dapat menggunakan fungsi-fungsi ini. Anda bisa menempatkan kode ini di dalam `main.py` untuk menjalankannya:

```python
import cloudscraper
import logging
from pathlib import Path
from scraper.report_scraper import get_inlineXBRL_attachments, get_inlineXBRL_zip_files, save_inlineXBRL_zip_files

# Konfigurasi logging dasar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    scraper = cloudscraper.create_scraper()
    
    try:
        # 1. Dapatkan iterator lampiran laporan XBRL
        logger.info("Mencari lampiran laporan inlineXBRL untuk tahun 2022, tipe 'rdf' (tahunan) periode 'audit'...")
        attachments_iterator = get_inlineXBRL_attachments(
            scraper,
            index_from=1,
            page_size=50, # Sesuaikan jumlah laporan per halaman
            year=2022,
            report_type='rdf', # 'rdf' untuk laporan tahunan/reguler, 'fs' untuk laporan keuangan
            periode='audit' # 'audit', 'q1', 'q2', 'q3'
        )
        
        # 2. Unduh konten file ZIP laporan
        logger.info("Mulai mengunduh file ZIP laporan...")
        files_iterator = get_inlineXBRL_zip_files(scraper, attachments_iterator, logger=logger)
        
        # 3. Simpan file ZIP yang telah diunduh ke direktori lokal
        output_directory = Path.cwd() / 'downloaded_reports'
        logger.info(f"Menyimpan file ke: {output_directory}")
        saved_filepaths = save_inlineXBRL_zip_files(str(output_directory), files_iterator, logger=logger)
        
        for filepath in saved_filepaths:
            logger.info(f"Berhasil menyimpan: {filepath}")
            
    except Exception as e:
        logger.error(f"Terjadi kesalahan selama proses scraping: {e}")
    finally:
        scraper.close()
        logger.info("Proses selesai.")
```

## Struktur Proyek

```
.
├── main.py                     # Titik masuk utama untuk menjalankan scraper. Anda dapat mengimplementasikan logika penggunaan di sini.
└── scraper/
    ├── __init__.py
    ├── report_scraper.py       # Berisi logika inti untuk melakukan scraping data dan pengunduhan file.
    └── test_report_scraper.py  # Berisi unit tests untuk memastikan fungsionalitas scraper berjalan dengan baik.
```