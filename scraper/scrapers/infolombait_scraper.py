import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from .base_scraper import BaseScraper

class InfolombaitScraper(BaseScraper):
    base_url = 'https://www.infolombait.com/'

    def __init__(self, max_page):
        super().__init__()
        self.max_page = max_page

    def traverse_url(self, title, url):
        print(f"Mengambil deskripsi lomba dari satu halaman: {url}" )

        data_lomba = {
            'title': title,
            'url': url
        }

        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            deskripsi_lomba_scope = soup.select_one('div.entry-content')

            if deskripsi_lomba_scope:
                print(f"\n✅ Berhasil menemukan deskripsi lomba:")

                deskripsi_lomba_tags = deskripsi_lomba_scope.select('p')
                print(f"\n--- Memulai Investigasi {len(deskripsi_lomba_tags)} Paragraf ---")

                final_description_parts = []

                for i, p_tag in enumerate(deskripsi_lomba_tags):
                    
                    text = ''

                    if not p_tag.get_text(strip=True):
                        final_description_parts.append('\n') 
                        continue
                    else:
                        text = p_tag.get_text(strip=True)
                        final_description_parts.append(text)

                    final_description_parts.append('\n') 

                deskripsi_lomba = ''.join(final_description_parts)

                deskripsi_lomba_bersih = re.sub(r'\n{3,}', '\n\n', deskripsi_lomba)

                data_lomba['description'] = deskripsi_lomba_bersih
                return data_lomba
            else:
                print("\n❌ Gagal menemukan deskripsi lomba dengan selector yang digunakan.")
                print("    Mungkin struktur HTML situs telah berubah. Perlu investigasi ulang.")

        except requests.exceptions.RequestException as e:
            print(f"\n❌ Gagal melakukan request ke URL. Error: {e}")
        except Exception as e:
            print(f"\n❌ Terjadi sebuah error: {e}")

    def scrape(self):
        print(f"Mengambil daftar lomba dari halaman utama: {self.base_url}" )

        page_count = 0
        next_page_url = self.base_url
        while page_count < self.max_page:
            print(f"\n------HALAMAN {page_count + 1}------\n")
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

                    print(f"\n✅ Berhasil menemukan {len(list_lomba)} lomba:")
                    
                    batch_lomba_mentah = []

                    for lomba in list_lomba:
                        lomba_url_tag = lomba.select_one('h2.entry-title a');

                        lomba_title = lomba_url_tag.text.strip()
                        lomba_url = lomba_url_tag['href'];

                        print(f"  - Judul: {lomba_title}")
                        print(f"    Link: {lomba_url}")

                        data_mentah = self.traverse_url(lomba_title, lomba_url)
                        batch_lomba_mentah.append(data_mentah)
                        time.sleep(1.5)

                    for i in range(0, len(batch_lomba_mentah), self.BATCH_SIZE):
                        current_batch = batch_lomba_mentah[i:i + self.BATCH_SIZE]

                        batch_data_terstruktur = self.strukturkan_dengan_ai(current_batch)
                        
                        if batch_data_terstruktur:
                            for data_terstruktur in batch_data_terstruktur:
                                if data_terstruktur:
                                    print(json.dumps(data_terstruktur, indent=2, ensure_ascii=False))

                                    self.simpan_ke_db(data_terstruktur)
                        else:
                            print("⚠️ Panggilan AI gagal tanpa error spesifik, mencoba lagi...")
                    
                else:
                    print("\n❌ Gagal menemukan link lomba dengan selector yang digunakan.")
                    print("    Mungkin struktur HTML situs telah berubah. Perlu investigasi ulang.")

            except requests.exceptions.RequestException as e:
                print(f"\n❌ Gagal melakukan request ke URL. Error: {e}")
            except Exception as e:
                print(f"\n❌ Terjadi sebuah error: {e}")
            finally:

                page_count += 1
                last_timestamp = None 

                timestamp_tag = lomba_terakhir.select_one('abbr.published.timeago')
                if timestamp_tag:
                    last_timestamp = timestamp_tag['title']
                
                if last_timestamp:
                    encoded_timestamp = quote_plus(last_timestamp)
                    
                    next_page_url = f"https://www.infolombait.com/search?updated-max={encoded_timestamp}&max-results=6#PageNo={page_count + 1}"
                    print(f"\n--- Halaman berikutnya ditemukan: {next_page_url} ---" )

                else:
                    print("\n--- Tidak ada lagi halaman berikutnya. Proses selesai. ---")
                    break # Keluar dari loop 'while True:'