import os, json

from models import Base, Tag, get_engine_and_session

DB_FILENAME = "jangkau.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_FILENAME)
DATABASE_URL = f"sqlite:///{DB_PATH}"

TAGS_FILE_PATH = os.path.join(os.path.dirname(__file__), 'tags.json')

def load_initial_tags():
    """Membaca daftar tag dari file tags.json."""
    try:
        with open(TAGS_FILE_PATH, 'r', encoding='utf-8') as f:
            tags = json.load(f)
        return tags
    except FileNotFoundError:
        print(f"❌ Error: File '{TAGS_FILE_PATH}' tidak ditemukan.")
        return []
    except json.JSONDecodeError:
        print(f"❌ Error: Gagal mem-parsing JSON dari '{TAGS_FILE_PATH}'. Pastikan formatnya benar.")
        return []

def initialize_local_database():
    """
    Membuat dan mengisi database SQLite lokal untuk development.
    Menghapus database lama jika ada untuk memastikan skema terbaru.
    """
    print("--- Local Database Initializer & Seeder ---")

    INITIAL_TAGS = load_initial_tags()

    if not INITIAL_TAGS:
        print("⚠️ Tidak ada tag awal untuk dimuat. Proses inisialisasi tag dilewati.")
        return

    if os.path.exists(DB_PATH):
        print(f"⚠️ Found existing database at '{DB_PATH}'. Deleting it to ensure a fresh schema.")
        os.remove(DB_PATH)

    print(f"Creating new database at: {DATABASE_URL}")

    engine, Session = get_engine_and_session(DATABASE_URL)

    session = Session()

    try:
        print("\nCreating all tables based on models...")
        Base.metadata.create_all(engine)
        print("✅ All tables created successfully.")

        print("\nSeeding initial tags...")
        
        tag_objects = [Tag(name=tag_name) for tag_name in INITIAL_TAGS]
        
        session.add_all(tag_objects)
        
        session.commit()
        print(f"✅ Successfully added {len(INITIAL_TAGS)} initial tags.")

        print("\n--- Database initialization and seeding complete. ---")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    initialize_local_database()