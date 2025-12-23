from babel.dates import format_date
from datetime import datetime, date
import sqlite3, os

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