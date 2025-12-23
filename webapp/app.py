import os, sqlite3
from flask import Flask, render_template
from helpers import convert_to_id_date

current_file_path = os.path.abspath(__file__)
webapp_dir = os.path.dirname(current_file_path)
PROJECT_ROOT = os.path.dirname(webapp_dir)

DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'jangkau.db')

app = Flask(__name__)

app.jinja_env.filters["convert_to_id_date"] = convert_to_id_date

def get_db_connection():
    """Fungsi bantuan untuk membuat koneksi ke database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Route untuk halaman utama."""
    conn = get_db_connection()
    
    list_lomba = conn.execute('SELECT * FROM lomba ORDER BY created_at DESC LIMIT 6').fetchall()
    
    conn.close()
    
    return render_template('index.html', list_lomba = list_lomba)

# Perintah untuk menjalankan server pengembangan
if __name__ == '__main__':
    app.run(debug=True, port=5000)