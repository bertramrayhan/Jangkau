import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from .base_scraper import BaseScraper
from config.logging_config import logger

class InformasilombaScraper(BaseScraper):
    base_url = 'https://www.informasilomba.com/sitemap.xml'

    def __init__(self, max_page, max_competition):
        super().__init__()
        self.max_page = max_page
        self.max_competition = max_competition
        self.current_total_competition = 0

    def traverse_url(self, url):
        logger.info(f"Mengambil content lomba dari satu halaman: {url}")

        # data_lomba didefinisikan di awal, bagus.
        data_lomba = {'source_url': url}

        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            title_lomba_tag = soup.select_one('h1.entry-title')
            # Tambahkan pemeriksaan jika judul tidak ditemukan
            if not title_lomba_tag:
                logger.error(f"  -> ❌ Gagal menemukan judul untuk URL: {url}")
                return None
            data_lomba['title'] = title_lomba_tag.get_text(strip=True)

            content_lomba_body_scope = soup.select_one('div.entry-content')

            if content_lomba_body_scope:
                # Logika cerdas Anda untuk menemukan ID
                div_id = content_lomba_body_scope.get('id', '') # .get() lebih aman dari ['id']
                if 'post-body-' in div_id:
                    id_num = div_id.replace('post-body-', '')
                    
                    # Selector spesifik Anda
                    content_lomba_scope = soup.select_one(f'#post2{id_num}')

                    if content_lomba_scope:
                        data_lomba['content_html'] = content_lomba_scope.decode_contents()
                        logger.info('  -> ✅ Content berhasil ditemukan!')
                        return data_lomba # Mengembalikan data yang berhasil didapat
                    else:
                        logger.error(f"  -> ❌ Gagal menemukan #post2{id_num} di dalam {url}")
                        return None # Gagal, kembalikan None
                else:
                    # Fallback jika 'div.entry-content' tidak punya ID yang diharapkan
                    logger.warning(f"  -> ⚠️ 'div.entry-content' tidak memiliki ID 'post-body-'. Menggunakan kontennya langsung.")
                    data_lomba['content_html'] = content_lomba_body_scope.decode_contents()
                    return data_lomba
            else:
                logger.error(f"  -> ❌ Gagal menemukan 'div.entry-content' di {url}")
                return None # Gagal, kembalikan None

        except requests.exceptions.RequestException as e:
            logger.error(f"  -> ❌ Gagal request ke {url}. Error: {e}")
            return None
        except Exception as e:
            logger.error(f"  -> ❌ Terjadi error tak terduga saat memproses {url}. Error: {e}")
            return None

    def scrape(self):
        logger.info(f"Mengambil daftar lomba dari halaman utama: {self.base_url}" )

        try:
            response = requests.get(self.base_url, headers=self.HEADERS, timeout=15)
            response.raise_for_status() # Tambahkan ini untuk memeriksa error HTTP

            soup_index = BeautifulSoup(response.text, 'xml') 

            page_loc_tags = soup_index.find_all('loc')

            logger.info(f"Menemukan {len(page_loc_tags)} sitemap anak.")

            if not page_loc_tags:
                logger.error('tidak ditemukan link page')
                return

            for loc_tag in page_loc_tags[:self.max_page]:
                sitemap_url = loc_tag.get_text()
                logger.info(sitemap_url)

                response_page = requests.get(sitemap_url, headers=self.HEADERS, timeout=15)
                response_page.raise_for_status()

                soup_page = BeautifulSoup(response_page.text, 'xml') 

                page_lomba_loc_tags = soup_page.find_all('loc')

                logger.info(f"Menemukan {len(page_lomba_loc_tags)} link lomba pada sitemap {sitemap_url}.")

                if not page_lomba_loc_tags:
                    logger.error('tidak ditemukan link lomba')
                    return

                batch_lomba_mentah = []
                for lomba_loc_tag in page_lomba_loc_tags:
                    if self.current_total_competition == self.max_competition:
                        break

                    lomba_url = lomba_loc_tag.get_text()
                    logger.info(lomba_url)

                    data_mentah = self.traverse_url(lomba_url)
                    if data_mentah:  # Only add if data was successfully retrieved
                        batch_lomba_mentah.append(data_mentah)
                        logger.info("sebelum AI")
                        logger.info(data_mentah)
                        logger.info("------")
                        self.current_total_competition += 1

                # Filter out competitions that already exist in database
                filtered_batch = self.filter_existing_competitions(batch_lomba_mentah)
                
                if not filtered_batch:
                    logger.info("✅ Semua lomba dalam batch sudah ada di database. Melanjutkan ke sitemap berikutnya.")
                    continue

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

        except requests.exceptions.RequestException as e:
            logger.error(f"\n❌ Gagal melakukan request ke URL. Error: {e}")
        except Exception as e:
            logger.error(f"\n❌ Terjadi sebuah error: {e}")