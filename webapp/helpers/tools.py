from babel.dates import format_date
from datetime import datetime, date
import sqlite3, os
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv('DB_PATH')

def convert_to_id_date(value):
    if value is None:
        return "-"

    # kalo masih string dari SQLite
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value).date()
        except ValueError:
            return value  # fallback, biar gak crash

    if isinstance(value, (date, datetime)):
        return format_date(value, "d MMMM y", locale="id")

    return value

def get_db_connection():
    """Fungsi bantuan untuk membuat koneksi ke database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_db_path():
    return DB_PATH


def get_domain_from_url(url):
    """
    Mengekstrak nama domain bersih dari sebuah URL lengkap.
    Contoh: 'https://www.lomba-keren.com/path?query=1' -> 'lomba-keren.com'
    """
    if not url:
        return None
    try:
        # 1. Parse URL
        parsed_url = urlparse(url)
        
        # 2. Ambil netloc (e.g., 'www.lomba-keren.com')
        netloc = parsed_url.netloc
        
        # 3. Hapus 'www.' jika ada
        if netloc.startswith('www.'):
            netloc = netloc[4:]
            
        return netloc
    except Exception:
        # Jika URL tidak valid, kembalikan None
        return None