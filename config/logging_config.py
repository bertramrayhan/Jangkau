import logging
import os
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

def setup_logging():
    """
    Mengkonfigurasi sistem logging untuk seluruh aplikasi.
    Bisa diatur melalui variabel lingkungan APP_ENV.
    """
    app_env = os.getenv('APP_ENV', 'development')
    log_level = logging.DEBUG if app_env == 'development' else logging.INFO

    # 1. Buat logger utama untuk aplikasi 'jangkau'
    logger = logging.getLogger('jangkau')
    logger.setLevel(log_level)

    # Cegah duplikasi log jika fungsi ini dipanggil lebih dari sekali
    if logger.hasHandlers():
        logger.handlers.clear()

    # 2. Buat formatter untuk format pesan log
    # Format: [TIMESTAMP] [LEVEL] [NAMA_MODUL] PESAN
    log_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(module)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 3. Buat handler untuk output ke konsol (terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # 4. Buat handler untuk output ke file (jangkau.log)
    # RotatingFileHandler akan membuat file baru jika sudah terlalu besar
    log_file_path = os.path.join('logs', 'jangkau.log')
    
    # Pastikan direktori 'logs' ada
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # maxBytes=5MB, backupCount=3 -> jangkau.log, jangkau.log.1, jangkau.log.2
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    print(f"✅ Sistem logging berhasil dikonfigurasi. Mode: {app_env.upper()}. Log file: {log_file_path}")

    return logger

# Panggil setup sekali dan sediakan logger yang sudah dikonfigurasi
# Aplikasi lain tinggal mengimpor 'logger' dari file ini
logger = setup_logging()