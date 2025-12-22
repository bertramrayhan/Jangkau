from bs4 import BeautifulSoup
from google import genai
from google.genai import types
import json, os, sqlite3, time, requests, re
from urllib.parse import quote_plus

class JangkauScraper:
    def __init__(self):
        self.base_url = 'https://www.infolombait.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.DB_NAME = 'database/jangkau.db'
        self.BATCH_SIZE = 5
        self.MAX_PAGE = 5
        self.model_list = [
            # --- Pilihan Utama (Cepat dan Cukup Cerdas) ---
            'models/gemini-flash-latest',
            'models/gemini-2.5-flash',
            
            # --- Pilihan Kedua (Lebih Cerdas, Mungkin Sedikit Lebih Lambat) ---
            'models/gemini-pro-latest',
            'models/gemini-2.5-pro',
            
            # --- Pilihan Cadangan (Model Gemma, lebih kecil) ---
            # Mungkin tidak seakurat Gemini, tapi patut dicoba jika yang lain gagal
            'models/gemma-3-12b-it', 
            'models/gemma-3-4b-it',
        ]
        self.current_model_index = 0

    def simpan_ke_db(self, data_terstruktur):
        """Menyimpan data lomba yang sudah terstruktur ke database SQLite."""
        print(f"\n--- Menyimpan data untuk '{data_terstruktur.get('title', 'Tanpa Judul')}' ke database... ---")
        
        conn = None
        try:
            conn = sqlite3.connect(self.DB_NAME)
            cursor = conn.cursor()

            # --- LANGKAH 1: Masukkan data utama ke tabel 'lomba' ---
            
            # Perbaikan: Menambahkan semua kolom yang relevan
            sql_insert_lomba = """
            INSERT INTO lomba (
                title, source_url, raw_description, organizer, 
                registration_start, registration_end, event_start, event_end,
                is_free, price_details, location, location_details, registration_link
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Perbaikan: Menambahkan semua nilai yang sesuai ke dalam tuple
            lomba_data_tuple = (
                data_terstruktur.get('title'),
                data_terstruktur.get('source_url'),
                data_terstruktur.get('raw_description'),
                data_terstruktur.get('organizer'),
                data_terstruktur.get('registration_start'),
                data_terstruktur.get('registration_end'),
                data_terstruktur.get('event_start'),
                data_terstruktur.get('event_end'),
                data_terstruktur.get('is_free'),
                data_terstruktur.get('price_details'),
                data_terstruktur.get('location'),
                data_terstruktur.get('location_details'),
                data_terstruktur.get('registration_link')
            )
            
            url_sumber = data_terstruktur.get('source_url')
            # Eksekusi perintah SQL
            # Kita akan menggunakan pendekatan SELECT dulu untuk pesan log yang lebih baik
            cursor.execute("SELECT id FROM lomba WHERE source_url = ?", (url_sumber,))
            existing_lomba = cursor.fetchone()

            if existing_lomba:
                print(f"ℹ️ Data lomba dengan URL {url_sumber} sudah ada di database. Proses penyimpanan dilewati.")
                return

            cursor.execute(sql_insert_lomba, lomba_data_tuple)
            lomba_id = cursor.lastrowid
            
            # --- LANGKAH 2: Tangani Tags (Bagian Many-to-Many) ---
            tag_list = data_terstruktur.get('tags', [])
            if tag_list:
                for tag_name in tag_list:
                    # Dapatkan ID dari tag yang sudah ada (karena kita sudah pre-seed)
                    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                    tag_id_result = cursor.fetchone()
                    
                    if tag_id_result:
                        tag_id = tag_id_result[0]
                        # Buat relasi di tabel jembatan 'lomba_tags'
                        cursor.execute("INSERT OR IGNORE INTO lomba_tags (lomba_id, tag_id) VALUES (?, ?)", (lomba_id, tag_id))
                    else:
                        # Fallback jika AI memberikan tag yang tidak ada di daftar kita
                        print(f"⚠️ Peringatan: Tag '{tag_name}' dari AI tidak ditemukan di tabel 'tags'. Tag ini akan diabaikan.")

            conn.commit()
            print(f"✅ Data berhasil disimpan dengan ID Lomba: {lomba_id}")

        except sqlite3.Error as e:
            print(f"❌ Terjadi error database: {e}")
            if conn:
                conn.rollback()
                
        finally:
            if conn:
                conn.close()

    def get_batch_prompt(self, batch_lomba_mentah):
        batch_text_input = ""

        for lomba_mentah in batch_lomba_mentah:
            batch_text_input += f"""
            url : {lomba_mentah['url']}
            Judul : {lomba_mentah['title']}
            Deskrpsi : {lomba_mentah['description']}

            --- LOMBA BARU ---


            """

        # Daftar tag kita definisikan di sini agar mudah dikelola
        daftar_tag_valid = [
            "Programming", "Hackathon", "CTF", "Data Science", "UI/UX Design", 
            "Desain Grafis", "Business Case", "Debat", "Menulis Esai", "Robotika", 
            "Mahasiswa", "SMA", "Umum", "Gratis", "Berbayar", "Online", "Offline", "Hybrid"
        ]
        
        # Mengubah daftar tag menjadi string untuk dimasukkan ke dalam prompt
        tags_string = ", ".join([f'"{tag}"' for tag in daftar_tag_valid])

        return f"""
        PERAN: Anda adalah sebuah API pemrosesan batch yang sangat akurat. Tugas Anda adalah menerima serangkaian data acara, dan mengembalikan sebuah ARRAY JSON yang berisi hasil ekstraksi untuk SETIAP acara.

        INPUT:
        Serangkaian data acara di bawah ini. Setiap acara dipisahkan oleh "--- LOMBA BARU ---".
        ---
        {batch_text_input}
        ---

        TUGAS:
        Untuk SETIAP acara dalam INPUT, ekstrak informasinya ke dalam sebuah objek JSON. Gabungkan semua objek JSON tersebut ke dalam sebuah ARRAY JSON tunggal.

        ATURAN EKSTRAKSI (berlaku untuk setiap objek JSON):
        1.  **`id_lomba_input`**: WAJIB diisi dengan nomor ID yang tertera di input untuk setiap lomba. Tipe datanya harus integer.
        2.  **`title`**: WAJIB diisi dengan judul yang tertera di input untuk setiap lomba.
        3.  **Format Tanggal**: Gunakan format `YYYY-MM-DD`. Jika tahun tidak ada, asumsikan `2025` atau `2026` berdasarkan konteks. Jika tidak ada info tanggal, gunakan `null`.
        4.  **`is_free`**: Gunakan `true` jika teks menyebut 'GRATIS'/'FREE'. Gunakan `false` jika ada harga. Gunakan `null` jika tidak ada info biaya.
        5.  **`tags`**: Pilih beberapa tag yang paling relevan HANYA dari daftar berikut: [{tags_string}].
        6.  **`registration_link`**: Prioritaskan link dari platform seperti 'linktr.ee', 'bit.ly', atau yang mengandung kata 'daftar'/'register'. Jika tidak ada, gunakan `null`.
        7.  **Nilai `null`**: Untuk field lain, jika informasinya tidak dapat ditemukan, WAJIB gunakan nilai `null`.

        STRUKTUR WAJIB UNTUK SETIAP OBJEK JSON:
        {{
        "id_lomba_input": integer,
        "title": "string",
        "source_url": salin url pada lomba,
        "raw_description": salin deskripsi pada lomba,
        "organizer": "string atau null",
        "registration_start": "YYYY-MM-DD atau null",
        "registration_end": "YYYY-MM-DD atau null",
        "event_start": "YYYY-MM-DD atau null",
        "event_end": "YYYY-MM-DD atau null",
        "is_free": boolean atau null,
        "price_details": "string atau null",
        "location": "string ('Online', 'Offline', 'Hybrid') atau null",
        "location_details": "string atau null",
        "tags": ["array", "of", "strings"],
        "registration_link": "string (URL) atau null"
        }}

        ATURAN OUTPUT FINAL:
        Respons Anda HARUS HANYA berisi array JSON `[...]` yang valid. Jangan sertakan teks pembuka, penutup, markdown (```json), atau penjelasan apa pun.
        """

    def strukturkan_dengan_ai(self, batch_lomba_mentah):
        print("\n--- Menghubungi AI untuk menstrukturkan data (Cara Terbaru)... ---")
        
        if self.current_model_index >= len(self.model_list):
            print("❌ Semua model telah mencapai rate limit. Tidak bisa memproses batch ini.")
            return None

        current_model_name = self.model_list[self.current_model_index]
        print(f"\n--- Menghubungi AI (Mencoba Model: {current_model_name}) ---")

        prompt = self.get_batch_prompt(batch_lomba_mentah)
        
        max_retries_per_model = 5
        base_delay = 5
        for attempt in range(max_retries_per_model):
            try:
                client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

                response = client.models.generate_content(
                    model= current_model_name,
                    contents= prompt,
                    config= types.GenerateContentConfig(
                        response_mime_type='application/json'
                    )
                )
                
                batch_data_terstruktur = json.loads(response.text)
                
                print(f"✅ AI berhasil menstrukturkan batch dengan model {current_model_name}.")
                client.close()
                return batch_data_terstruktur
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "503" in str(e):
                    if attempt < max_retries_per_model - 1: # Cek jika ini bukan percobaan terakhir
                        wait_time = base_delay * (2 ** attempt)
                        print(f"⚠️ API Error. Menunggu {wait_time} detik... (Percobaan {attempt + 1}/{max_retries_per_model})")
                        time.sleep(wait_time)
                    else:
                        self.current_model_index += 1
                        # Jika ini percobaan terakhir, cetak pesan dan biarkan loop berakhir
                        print(f"❌ Gagal total pada model '{current_model_name}'. Merotasi ke model berikutnya...")
                        return self.strukturkan_dengan_ai(batch_lomba_mentah)
                else:
                    # Jika error lain, langsung keluar dan kembalikan None
                    print(f"❌ Terjadi error tak terduga: {e}")
                    return None # Langsung return None, jangan break
        return None

    def traverse_url(self, title, url):
        print(f"Mengambil deskripsi lomba dari satu halaman: {url}" )

        data_lomba = {
            'title': title,
            'url': url
        }

        try:
            response = requests.get(url, headers=self.headers, timeout=15)
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

    def run(self):
        print(f"Mengambil daftar lomba dari halaman utama: {self.base_url}" )

        page_count = 0
        next_page_url = self.base_url
        while page_count < self.MAX_PAGE:
            print(f"\n------HALAMAN {page_count + 1}------\n")
            lomba_terakhir = None
            try:
                response = requests.get(next_page_url, headers=self.headers, timeout=15)
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