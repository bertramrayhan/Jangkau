import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from .base_scraper import BaseScraper
from config.logging_config import logger

class InfolombaitScraper(BaseScraper):
    base_url = 'https://www.infolombait.com/'

    def __init__(self, max_page):
        super().__init__()
        self.max_page = max_page

    def traverse_url(self, title, url):
        logger.info(f"Mengambil content lomba dari satu halaman: {url}" )

        data_lomba = {
            'title': title,
            'source_url': url
        }

        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            content_lomba_scope = soup.select_one('div.entry-content')

            if content_lomba_scope:
                logger.info(f"\n✅ Berhasil menemukan content lomba:")

                data_lomba['content_html'] = content_lomba_scope.decode_contents()

                return data_lomba
            else:
                logger.error("\n❌ Gagal menemukan deskripsi lomba dengan selector yang digunakan.")
                logger.error("    Mungkin struktur HTML situs telah berubah. Perlu investigasi ulang.")

        except requests.exceptions.RequestException as e:
            logger.error(f"\n❌ Gagal melakukan request ke URL. Error: {e}")
        except Exception as e:
            logger.error(f"\n❌ Terjadi sebuah error: {e}")

    def scrape(self):
        logger.info(f"Mengambil daftar lomba dari halaman utama: {self.base_url}" )

        page_count = 0
        next_page_url = self.base_url
        while page_count < self.max_page:
            logger.info(f"\n------HALAMAN {page_count + 1}------\n")
            lomba_terakhir = None
            try:
                response = requests.get(next_page_url, headers=self.HEADERS, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                
                list_lomba = soup.select('article')

                if list_lomba:
                    if page_count == 0:
                        lomba_terakhir = list_lomba[5]
                    else:
                        lomba_terakhir = list_lomba[-1]

                    logger.info(f"\n✅ Berhasil menemukan {len(list_lomba)} lomba:")
                    
                    batch_lomba_mentah = []

                    for lomba in list_lomba:
                        lomba_url_tag = lomba.select_one('h2.entry-title a');

                        lomba_title = lomba_url_tag.text.strip()
                        lomba_url = lomba_url_tag['href'];

                        logger.info(f"  - Judul: {lomba_title}")
                        logger.info(f"    Link: {lomba_url}")

                        data_mentah = self.traverse_url(lomba_title, lomba_url)
                        if data_mentah:  # Only add if data was successfully retrieved
                            batch_lomba_mentah.append(data_mentah)
                        time.sleep(1.5)

                    # Filter out competitions that already exist in database
                    filtered_batch = self.filter_existing_competitions(batch_lomba_mentah)
                    
                    if not filtered_batch:
                        logger.info("✅ Semua lomba dalam batch sudah ada di database. Melanjutkan ke halaman berikutnya.")
                    else:
                        for i in range(0, len(filtered_batch), self.BATCH_SIZE):
                            current_batch = filtered_batch[i:i + self.BATCH_SIZE]

                            batch_data_terstruktur = self.strukturkan_dengan_ai(current_batch)
                            
                            if batch_data_terstruktur:
                                for data_terstruktur in batch_data_terstruktur:
                                    if data_terstruktur:
                                        logger.info(json.dumps(data_terstruktur, indent=2, ensure_ascii=False))

                                        self.simpan_ke_db(data_terstruktur)
                            else:
                                logger.warning("⚠️ Panggilan AI gagal tanpa error spesifik, mencoba lagi...")
                    
                else:
                    logger.error("\n❌ Gagal menemukan link lomba dengan selector yang digunakan.")
                    logger.error("    Mungkin struktur HTML situs telah berubah. Perlu investigasi ulang.")

            except requests.exceptions.RequestException as e:
                logger.error(f"\n❌ Gagal melakukan request ke URL. Error: {e}")
            except Exception as e:
                logger.error(f"\n❌ Terjadi sebuah error: {e}")
            finally:

                page_count += 1
                last_timestamp = None 

                timestamp_tag = lomba_terakhir.select_one('abbr.published.timeago')
                if timestamp_tag:
                    last_timestamp = timestamp_tag['title']
                
                if last_timestamp:
                    encoded_timestamp = quote_plus(last_timestamp)
                    
                    next_page_url = f"https://www.infolombait.com/search?updated-max={encoded_timestamp}&max-results=6#PageNo={page_count + 1}"
                    logger.info(f"\n--- Halaman berikutnya ditemukan: {next_page_url} ---" )

                else:
                    logger.info("\n--- Tidak ada lagi halaman berikutnya. Proses selesai. ---")
                    break # Keluar dari loop 'while True:'