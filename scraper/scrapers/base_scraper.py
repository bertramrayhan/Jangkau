import os, sys, json, time, bleach
from abc import ABC, abstractmethod
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import Date, DateTime
from config.logging_config import logger

# --- Path setup ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(root_dir)

from database.models import Lomba, Tag, get_engine_and_session
from scraper.ai.manager import AIManager

class BaseScraper(ABC):
    HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    BATCH_SIZE = 3
    ALLOWED_TAGS = [
        'h2', 'h3', 'h4', 'h5', 'h6',
        'strong', 'b', # Tebal
        'em', 'i',     # Miring
        'u',          # Garis bawah
        'strike', 's',# Coret
        'ul', 'ol', 'li',
        'p',          # Paragraf
        'br',         # Baris baru
        'a',          # Link
        'blockquote', # Kutipan
        'table', 'thead', 'tbody', 'tr', 'th', 'td' # Menambahkan dukungan untuk tabel
    ]

    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title', 'width', 'height'], # Izinkan width/height untuk gambar
    }

    AI_MANAGER = AIManager()

    def __init__(self):
        """
        Konstruktor umum yang menangani koneksi database dan konfigurasi AI.
        """
        load_dotenv()
        
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

            untrusted_html = data_terstruktur.get('content_html')

            if untrusted_html:
                logger.info("  -> Melakukan sanitasi HTML dengan bleach...")
            
                safe_html = bleach.clean(
                    untrusted_html,
                    tags=self.ALLOWED_TAGS,
                    attributes=self.ALLOWED_ATTRIBUTES,
                    strip=True
                )
                
                data_terstruktur['content_html'] = safe_html
                logger.info("  -> ✅ Sanitasi HTML selesai.")

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

    def filter_existing_competitions(self, batch_lomba_mentah):
        """
        Filter out competitions that already exist in the database based on source_url.
        Returns only new competitions that need to be processed.
        """
        if not batch_lomba_mentah:
            logger.warning("⚠️ Batch kosong, tidak ada yang perlu difilter.")
            return []
        
        session = self.Session()
        new_competitions = []
        
        try:
            for lomba in batch_lomba_mentah:
                if not lomba or not lomba.get('source_url'):
                    logger.warning("⚠️ Data lomba tidak valid atau tidak memiliki source_url, dilewati.")
                    continue
                
                source_url = lomba.get('source_url')
                existing_lomba = session.query(Lomba).filter_by(source_url=source_url).first()
                
                if existing_lomba:
                    logger.info(f"ℹ️ Lomba '{lomba.get('title', 'Tanpa Judul')}' sudah ada di database (ID: {existing_lomba.id}). Dilewati dari proses AI.")
                else:
                    new_competitions.append(lomba)
                    logger.info(f"✅ Lomba '{lomba.get('title', 'Tanpa Judul')}' belum ada di database, akan diproses AI.")
            
            logger.info(f"📊 Hasil filtering: {len(new_competitions)} lomba baru dari {len(batch_lomba_mentah)} total lomba.")
            return new_competitions
            
        except Exception as e:
            logger.error(f"❌ Terjadi error saat filtering lomba: {e}")
            return batch_lomba_mentah  # Return original batch if filtering fails
        finally:
            session.close()

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