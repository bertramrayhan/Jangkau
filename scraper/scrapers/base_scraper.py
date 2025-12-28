import os
import sys
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types
from sqlalchemy import Date, DateTime
from config.logging_config import logger

# --- Path setup ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(root_dir)

from database.models import Lomba, Tag, get_engine_and_session

class BaseScraper(ABC):
    HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    BATCH_SIZE = 5
    MODEL_LIST = [
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

    def __init__(self):
        """
        Konstruktor umum yang menangani koneksi database dan konfigurasi AI.
        """
        load_dotenv()

        # State dinamis yang unik untuk setiap instance
        self.current_model_index = 0
        
        # --- Konfigurasi Database ---
        APP_ENV = os.getenv('APP_ENV', 'development').lower()
        self.DATABASE_URL = None 

        if APP_ENV == 'production':
            logger.info(f"🚀 {self.__class__.__name__} running in PRODUCTION mode.")
            self.DATABASE_URL = os.getenv('DATABASE_URL')
            if not self.DATABASE_URL:
                raise ValueError("❌ ERROR: DATABASE_URL must be set in production environment!")
            if self.DATABASE_URL.startswith("postgres://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        else: # (development)
            logger.info(f"💻 {self.__class__.__name__} running in DEVELOPMENT mode.")
            
            # 1. Buat path relatif langsung dari direktori kerja (root proyek).
            relative_db_path = os.path.join('database', 'jangkau.db')
            
            # 2. Ubah menjadi path absolut untuk kepastian.
            absolute_db_path = os.path.abspath(relative_db_path)
            
            # 3. Buat URL database.
            self.DATABASE_URL = f"sqlite:///{absolute_db_path}"

        if not self.DATABASE_URL:
            raise ValueError("❌ ERROR: Could not determine DATABASE_URL!")

        # Gunakan properti instance untuk membuat engine dan session
        self.engine, self.Session = get_engine_and_session(self.DATABASE_URL)
        
        logger.info(f"Scraper terhubung ke database: {self.engine.url.database}")

        self.VALID_TAGS = self._get_valid_tags()
        if self.VALID_TAGS:
            logger.info(f"   -> Berhasil memuat {len(self.VALID_TAGS)} tag yang valid dari database.")
        else:
            logger.warning("   -> ⚠️ Peringatan: Tidak ada tag yang dimuat dari database.")

    def _get_valid_tags(self):
        """Mengambil semua tag dari database satu kali saat inisialisasi."""
        session = self.Session()
        try:
            tags = session.query(Tag).all()
            return [tag.name for tag in tags] # Kembalikan daftar string nama tag
        except Exception as e:
            logger.error(f"❌ Terjadi error saat memuat tag dari database: {e}")
            return []
        finally:
            session.close()

    def simpan_ke_db(self, data_terstruktur):
        """
        Menyimpan data lomba yang sudah terstruktur ke database menggunakan SQLAlchemy.
        Metode ini bersifat 'agnostik' terhadap database (bisa SQLite atau PostgreSQL).
        """
        logger.info(f"\n--- Menyimpan '{data_terstruktur.get('title', 'Tanpa Judul')}' via SQLAlchemy... ---")
        
        session = self.Session()
        
        try:
            url_sumber = data_terstruktur.get('source_url')
            if not url_sumber:
                logger.warning("⚠️ Peringatan: Data tidak memiliki 'source_url'. Dilewati.")
                session.close()
                return

            existing_lomba = session.query(Lomba).filter_by(source_url=url_sumber).first()
            
            if existing_lomba:
                logger.info(f"ℹ️ Lomba dengan URL ini sudah ada (ID: {existing_lomba.id}). Dilewati.")
                session.close()
                return

            for col in Lomba.__table__.columns:
                if isinstance(col.type, (Date, DateTime)):
                    col_name = col.name
                    date_str = data_terstruktur.get(col_name)
                    
                    if isinstance(date_str, str):
                        try:
                            data_terstruktur[col_name] = datetime.strptime(date_str, '%Y-%m-%d').date()
                        except ValueError:
                            logger.warning(f"⚠️ Peringatan: Format tanggal salah untuk '{col_name}': '{date_str}'. Menggunakan null.")
                            data_terstruktur[col_name] = None

            data_terstruktur.pop('id_lomba_input')

            tags_from_ai = data_terstruktur.pop('tags', [])

            lomba_baru = Lomba(**data_terstruktur)

            if tags_from_ai:
                valid_tags = session.query(Tag).filter(Tag.name.in_(tags_from_ai)).all()
                
                if valid_tags:
                    lomba_baru.tags.extend(valid_tags)
                    
                    found_tag_names = {tag.name for tag in valid_tags}
                    logger.info(f"  -> Menambahkan relasi dengan tags: {', '.join(found_tag_names)}")

            session.add(lomba_baru)
            
            session.commit()
            
            logger.info(f"✅ Data berhasil disimpan dengan ID Lomba baru: {lomba_baru.id}")

        except Exception as e:
            logger.error(f"❌ Terjadi error database saat menyimpan: {e}")
            session.rollback()
        finally:
            session.close()

    def get_batch_prompt(self, batch_lomba_mentah):
        batch_text_input = ""

        for lomba_mentah in batch_lomba_mentah:
            batch_text_input += f"""
            url : {lomba_mentah['url']}
            Judul : {lomba_mentah['title']}
            Deskrpsi : {lomba_mentah['description']}

            --- LOMBA BARU ---


            """

        # Mengubah daftar tag menjadi string untuk dimasukkan ke dalam prompt
        tags_string = ", ".join([f'"{tag_name}"' for tag_name in self.VALID_TAGS])

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
        logger.info("\n--- Menghubungi AI untuk menstrukturkan data (Cara Terbaru)... ---")
        
        if self.current_model_index >= len(self.MODEL_LIST):
            logger.error("❌ Semua model telah mencapai rate limit. Tidak bisa memproses batch ini.")
            return None

        current_model_name = self.MODEL_LIST[self.current_model_index]
        logger.info(f"\n--- Menghubungi AI (Mencoba Model: {current_model_name}) ---")

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
                
                logger.info(f"✅ AI berhasil menstrukturkan batch dengan model {current_model_name}.")
                client.close()
                return batch_data_terstruktur
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "503" in str(e):
                    if attempt < max_retries_per_model - 1: # Cek jika ini bukan percobaan terakhir
                        wait_time = base_delay * (2 ** attempt)
                        logger.warning(f"⚠️ API Error. Menunggu {wait_time} detik... (Percobaan {attempt + 1}/{max_retries_per_model})")
                        time.sleep(wait_time)
                    else:
                        self.current_model_index += 1
                        # Jika ini percobaan terakhir, cetak pesan dan biarkan loop berakhir
                        logger.warning(f"❌ Gagal total pada model '{current_model_name}'. Merotasi ke model berikutnya...")
                        return self.strukturkan_dengan_ai(batch_lomba_mentah)
                else:
                    # Jika error lain, langsung keluar dan kembalikan None
                    logger.error(f"❌ Terjadi error tak terduga: {e}")
                    return None # Langsung return None, jangan break
        return None

    # --- Metode dan properti Abstrak (Wajib diimplementasikan oleh anak) ---

    @property
    @abstractmethod
    def base_url(self):
        """
        Setiap scraper spesialis WAJIB mendefinisikan URL dasar
        situs yang akan di-scrape.
        """
        pass

    @abstractmethod
    def scrape(self):
        """
        Metode utama yang harus diimplementasikan oleh setiap scraper spesialis.
        Tugasnya adalah melakukan scraping dan memanggil metode umum seperti
        strukturkan_dengan_ai() dan simpan_ke_db().
        """
        pass