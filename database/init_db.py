import sqlite3, os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

DB_PATH = os.getenv('DB_PATH')
print(DB_PATH)

INITIAL_TAGS = [
    "Programming", "Hackathon", "CTF", "Data Science", "UI/UX Design", 
    "Desain Grafis", "Business Case", "Debat", "Menulis Esai", "Robotika", 
    "Mahasiswa", "SMA", "Umum", "Gratis", "Berbayar", "Online", "Offline", "Hybrid"
]

def create_tables():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        print(f"📁 Membuat direktori: {db_dir}")
        os.makedirs(db_dir)
        os.makedirs(db_dir)
    
    # SQL untuk drop tabel jika sudah ada (dalam urutan yang benar untuk foreign keys)
    sql_drop_lomba_tags_table = "DROP TABLE IF EXISTS lomba_tags;"
    sql_drop_lomba_table = "DROP TABLE IF EXISTS lomba;"
    sql_drop_tags_table = "DROP TABLE IF EXISTS tags;"
        
    sql_create_lomba_table = """
    CREATE TABLE IF NOT EXISTS lomba (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        source_url TEXT NOT NULL UNIQUE,
        raw_description TEXT,
        organizer TEXT,
        registration_start DATE,
        registration_end DATE,
        event_start DATE,
        event_end DATE,
        is_free BOOLEAN,
        price_details TEXT,
        location TEXT,
        location_details TEXT,
        registration_link TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    sql_create_tags_table = """
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """

    sql_create_lomba_tags_table = """
    CREATE TABLE IF NOT EXISTS lomba_tags (
        lomba_id INTEGER,
        tag_id INTEGER,
        PRIMARY KEY (lomba_id, tag_id),
        FOREIGN KEY (lomba_id) REFERENCES lomba (id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
    );
    """

    try:
        # Membuat koneksi ke database
        conn = sqlite3.connect(DB_PATH)
        print(f"Berhasil terhubung ke database '{DB_PATH}'")
        
        # Membuat objek cursor
        cursor = conn.cursor()
        
        # Drop semua tabel yang ada (dalam urutan yang benar untuk foreign keys)
        print("Menghapus tabel yang ada...")
        cursor.execute(sql_drop_lomba_tags_table)
        print("Tabel 'lomba_tags' dihapus (jika ada)")
        
        cursor.execute(sql_drop_lomba_table)
        print("Tabel 'lomba' dihapus (jika ada)")
        
        cursor.execute(sql_drop_tags_table)
        print("Tabel 'tags' dihapus (jika ada)")
        
        print("\nMembuat ulang semua tabel...")
        
        print("Membuat tabel 'lomba'...")
        cursor.execute(sql_create_lomba_table)
        
        print("Membuat tabel 'tags'...")
        cursor.execute(sql_create_tags_table)
        
        print("Membuat tabel 'lomba_tags'...")
        cursor.execute(sql_create_lomba_tags_table)
        
        print("\nMemasukkan daftar tag awal ke tabel 'tags'...")
        
        tags_to_insert = [(tag,) for tag in INITIAL_TAGS]
        
        cursor.executemany("INSERT OR IGNORE INTO tags (name) VALUES (?)", tags_to_insert)
        
        print(f"✅ Berhasil memasukkan/memverifikasi {len(tags_to_insert)} tag.")
        
        conn.commit()
        print("✅ Semua tabel dan data awal berhasil disiapkan.")
        
    except sqlite3.Error as e:
        print(f"❌ Terjadi error saat membuat tabel: {e}")
        
    finally:
        # Menutup koneksi
        if conn:
            conn.close()
            print("Koneksi ke database ditutup.")

if __name__ == '__main__':
    create_tables()
