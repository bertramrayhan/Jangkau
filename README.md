# Jangkau 🎯

<p align="center">
  <strong>Temukan Peluang Prestasimu Berikutnya</strong>
  <br>
  Satu tempat untuk semua informasi lomba, beasiswa, dan kompetisi di seluruh Indonesia.
</p>

<p align="center"> 
  <a href="#live-website">Live Website</a> •
  <a href="#screenshot">Screenshot</a> •
  <a href="#fitur">Fitur</a> •
  <a href="#instalasi">Instalasi</a> •
  <a href="#kontribusi">Kontribusi</a>
</p>

<p align="center">
  <a href="https://github.com/bertramrayhan/Jangkau/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/bertramrayhan/Jangkau?style=flat-square" alt="License"/>
  </a>
  <img src="https://img.shields.io/github/stars/bertramrayhan/Jangkau?style=flat-square" alt="Stars"/>
  <img src="https://img.shields.io/github/forks/bertramrayhan/Jangkau?style=flat-square" alt="Forks"/>
</p>

---

## 📋 Daftar Isi

- [Live Website](#live-website)
- [Screenshot](#screenshot)
- [Tentang Proyek](#tentang-proyek)
- [Fitur](#fitur)
- [Teknologi](#teknologi)
- [Struktur Proyek](#struktur-proyek)
- [Instalasi](#instalasi)
- [Penggunaan](#penggunaan)
- [API & Database](#api--database)
- [Scraper](#scraper)
- [Deployment](#deployment)
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)

## 🌐 Live Website

🚀 **[Akses Jangkau](https://jangkau-id.vercel.app)** 

Platform sudah live dan dapat diakses secara langsung. Untuk development lokal, ikuti [panduan instalasi](#instalasi) di bawah.

---

## 🖼️ Screenshot

### 🏠 Halaman Utama
![Halaman Utama](https://raw.githubusercontent.com/bertramrayhan/Jangkau/assets/homepage.png)
*Tampilan halaman utama dengan fitur pencarian dan filter*

### 📋 Halaman Detail
![Halaman Detail](https://raw.githubusercontent.com/bertramrayhan/Jangkau/assets/detail.png)
*Tampilan detail lomba dengan informasi lengkap dan link pendaftaran*

---

## 🎯 Tentang Proyek

**Jangkau** adalah platform web yang mengagregasi informasi lomba, kompetisi, dan beasiswa dari berbagai sumber di Indonesia. Platform ini dirancang untuk membantu mahasiswa dan pelajar menemukan peluang pengembangan diri dengan mudah dan terpusat.

### Mengapa Jangkau?

- **Informasi Tersebar**: Informasi lomba dan beasiswa sering tersebar di berbagai platform
- **Sulit Dicari**: Proses pencarian yang memakan waktu dan tidak efisien  
- **Terlewat Deadline**: Sering melewatkan peluang karena tidak tahu informasi terbaru
- **Tidak Terstruktur**: Informasi yang tidak terorganisir dengan baik

**Jangkau** hadir sebagai solusi dengan menyediakan:
- ✅ **Satu Platform Terpusat** untuk semua informasi
- ✅ **Pencarian & Filter Canggih** berdasarkan kategori, lokasi, dan tanggal
- ✅ **Informasi Terstruktur** dengan detail lengkap
- ✅ **Update Otomatis** melalui sistem scraping

## ✨ Fitur

### 🔍 Fitur Utama
- **Pencarian Lomba**: Cari lomba berdasarkan nama, kategori, atau penyelenggara
- **Filter Canggih**: Filter berdasarkan lokasi, jenis (gratis/berbayar), dan kategori
- **Detail Lengkap**: Informasi komprehensif setiap lomba termasuk:
  - Tanggal pendaftaran dan pelaksanaan
  - Lokasi dan detail tempat
  - Biaya pendaftaran
  - Link pendaftaran resmi
  - Tag kategori
- **Responsive Design**: Optimized untuk desktop, tablet, dan mobile

### 🔧 Fitur Teknis
- **Auto Scraping**: Sistem otomatis mengumpulkan data lomba dari sumber terpercaya
- **AI Processing**: Menggunakan Google Gemini AI untuk strukturisasi data
- **Database Sync**: Sinkronisasi otomatis antara development dan production
- **Multi-Environment**: Mendukung development (SQLite) dan production (PostgreSQL)

## 🛠 Teknologi

### Backend
- **Flask** - Web framework Python yang ringan dan fleksibel
- **SQLAlchemy** - ORM untuk manajemen database
- **PostgreSQL** - Database production
- **SQLite** - Database development

### Frontend  
- **Jinja2** - Template engine untuk Flask
- **TailwindCSS** - Utility-first CSS framework
- **HTMX** - Modern interactivity dengan minimal JavaScript
- **Material Symbols** - Icon library dari Google

### Data Processing
- **BeautifulSoup** - Web scraping library
- **Google Gemini AI** - AI untuk strukturisasi data
- **Requests** - HTTP library untuk web requests

### Tools & Utilities
- **Python-dotenv** - Environment variables management
- **Babel** - Internationalization (i18n)
- **PostCSS & Autoprefixer** - CSS processing
- **Pre-commit** - Code quality hooks

## 📁 Struktur Proyek

```
Jangkau/
├── 📁 database/           # Database dan model data
│   ├── init_db.py        # Inisialisasi database lokal
│   ├── models.py         # Model SQLAlchemy untuk scraper
│   ├── models_flask.py   # Model Flask-SQLAlchemy
│   └── jangkau.db        # Database SQLite (development)
│
├── 📁 scraper/            # Sistem web scraping
│   ├── main.py           # Entry point scraper
│   ├── scraper.py        # Logic utama scraping
│   ├── test_db.py        # Testing koneksi database
│   └── 📁 tools/         # Utilitas scraper
│       └── cek_model.py  # Checker model database
│
├── 📁 webapp/             # Aplikasi web Flask
│   ├── app.py            # Aplikasi utama Flask
│   ├── models.py         # Model Flask (auto-sync)
│   ├── requirements.txt  # Dependencies Flask
│   │
│   ├── 📁 helpers/       # Utilitas dan helper functions
│   │   ├── __init__.py
│   │   └── tools.py      # Filter Jinja2 dan utilities
│   │
│   ├── 📁 routes/        # Blueprint routing Flask
│   │   ├── __init__.py
│   │   ├── home.py       # Route halaman utama
│   │   └── detail.py     # Route halaman detail lomba
│   │
│   ├── 📁 static/        # Asset statis
│   │   └── 📁 css/
│   │       ├── input.css     # Input TailwindCSS
│   │       ├── output.css    # Compiled CSS
│   │       └── style.css     # Custom CSS
│   │
│   └── 📁 templates/     # Template Jinja2
│       ├── index.html        # Halaman utama
│       ├── detail.html       # Detail lomba
│       ├── tentang.html      # Halaman tentang
│       ├── 404.html          # Error page
│       │
│       ├── 📁 layouts/   # Layout templates
│       │   └── base.html # Base template
│       │
│       └── 📁 partials/  # Partial templates
│           ├── content.html  # Content component
│           ├── footer.html   # Footer component
│           └── navbar.html   # Navigation component
│
├── 📄 sync_models.py      # Sinkronisasi model database
├── 📄 package.json        # Dependencies Node.js (TailwindCSS)
├── 📄 tailwind.config.js  # Konfigurasi TailwindCSS
├── 📄 postcss.config.cjs  # Konfigurasi PostCSS  
├── 📄 requirements.txt    # Dependencies Python utama
└── 📄 README.md          # Dokumentasi proyek ini
```

## 🚀 Instalasi

### ⚡ Quick Start
```bash
# Clone & setup dalam 3 langkah
git clone https://github.com/bertramrayhan/Jangkau.git
cd Jangkau && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && cd database && python init_db.py
```

### Prasyarat
- **Python 3.8+**
- **Node.js 16+** (untuk TailwindCSS)
- **Git**

### 1. Clone Repository
```bash
git clone https://github.com/bertramrayhan/Jangkau.git
cd Jangkau
```

### 2. Setup Python Environment
```bash
# Buat virtual environment
python -m venv venv

# Aktivasi virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r webapp/requirements.txt
```

### 3. Setup Node.js Dependencies
```bash
npm install
```

### 4. Environment Variables
Buat file `.env` di root directory:
```env
# Database
APP_ENV=development
SECRET_KEY=your-secret-key-here

# AI Processing (opsional, untuk scraper)
GOOGLE_AI_API_KEY=your-gemini-api-key

# Database Production (jika diperlukan)
DATABASE_URL=postgresql://user:password@localhost/jangkau
```

### 5. Inisialisasi Database
```bash
cd database
python init_db.py
cd ..
```

### 6. Build CSS
```bash
npm run build
```

## 🎮 Penggunaan

### Development Mode

#### 1. Jalankan CSS Watcher (Terminal 1)
```bash
npm run dev
```

#### 2. Jalankan Flask App (Terminal 2)  
```bash
cd webapp
python app.py
```

#### 3. Akses Aplikasi
Buka browser dan kunjungi: `http://localhost:5000`

### Production Build
```bash
# Build CSS untuk production
npm run build

# Set environment
export APP_ENV=production

# Jalankan aplikasi
cd webapp
python app.py
```

### Menjalankan Scraper
```bash
# Pastikan sudah set GOOGLE_AI_API_KEY di .env
cd scraper
python main.py
```

## 💾 API & Database

### Model Database

#### Tabel Lomba (`lomba`)
```sql
- id (Primary Key)
- title (String, Not Null)
- source_url (String, Unique, Not Null) 
- raw_description (Text)
- organizer (String)
- registration_start (Date)
- registration_end (Date) 
- event_start (Date)
- event_end (Date)
- is_free (Boolean)
- price_details (Text)
- location (String)
- location_details (Text)
- registration_link (String)
- created_at (DateTime)
- updated_at (DateTime)
```

#### Tabel Tag (`tags`)
```sql  
- id (Primary Key)
- name (String, Unique, Not Null)
```

#### Relasi Many-to-Many (`lomba_tags`)
```sql
- lomba_id (Foreign Key -> lomba.id)
- tag_id (Foreign Key -> tags.id)
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Halaman utama dengan daftar lomba |
| `GET` | `/detail/<int:lomba_id>` | Detail lomba berdasarkan ID |
| `GET` | `/tentang` | Halaman tentang Jangkau |
| `GET` | `*` | 404 error handler |

### Query Parameters
- `q` - Pencarian teks
- `tags` - Filter berdasarkan tag (multiple)
- `tipe_lomba` - Filter gratis/berbayar (`gratis`, `berbayar`)
- `lokasi` - Filter berdasarkan lokasi

## 🕷 Scraper

Sistem scraper otomatis yang mengumpulkan data lomba dari berbagai sumber:

### Fitur Scraper
- **Multi-source**: Scraping dari InfoLombaIT dan sumber lainnya
- **AI Processing**: Menggunakan Google Gemini untuk strukturisasi data
- **Batch Processing**: Memproses multiple lomba sekaligus
- **Duplicate Detection**: Mencegah duplikasi berdasarkan `source_url`
- **Auto-tagging**: Otomatis menambahkan tag yang relevan

### Cara Kerja
1. **Crawling**: Mengambil daftar lomba dari halaman sumber
2. **Content Extraction**: Ekstrak detail dari setiap halaman lomba
3. **AI Processing**: Strukturisasi data menggunakan Gemini AI
4. **Database Storage**: Simpan ke database dengan pengecekan duplikasi

### Menjalankan Scraper
```bash
# Setup environment variable
export GOOGLE_AI_API_KEY=your-api-key

# Jalankan scraper
cd scraper  
python main.py
```

## 🌐 Deployment

### Development
Aplikasi menggunakan SQLite dan berjalan di `localhost:5000`

### Production  
Aplikasi menggunakan PostgreSQL dan dapat di-deploy ke:
- **Vercel** (recommended)
- **Heroku** 
- **Railway**
- **DigitalOcean**

### Environment Variables Production
```env
APP_ENV=production
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=production-secret-key
GOOGLE_AI_API_KEY=your-gemini-api-key
```

## 🤝 Kontribusi

Yuk ikut bantu develop Jangkau! Project ini dibuat untuk mahasiswa Indonesia, jadi semua kontribusi dari teman-teman sangat berarti 🙏

### 🚀 Quick Start

```bash
# 1. Fork & Clone
git clone https://github.com/[username-kamu]/Jangkau.git
cd Jangkau

# 2. Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && pip install -r webapp/requirements.txt
npm install && cp .env.example .env

# 3. Run
npm run dev  # Terminal 1
cd webapp && python app.py  # Terminal 2

# 4. Code & Submit PR! 
```

### 💡 Cara Kontribusi
- 🐛 **Bug Reports** - Nemu bug? Report aja di Issues  
- ✨ **Feature Ideas** - Punya ide keren? Share di Issues
- 💻 **Code** - Frontend, backend, scraper, semuanya welcome!
- 📚 **Docs** - Bantu improve dokumentasi
- 🌐 **Website Sources** - Saran website sumber lomba yang bagus

### 📖 Panduan Lengkap
Lihat **[CONTRIBUTING.md](./CONTRIBUTING.md)** untuk panduan detail, tapi santai aja—nggak serumit yang dibayangkan! 😄

## 📝 Lisensi

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📞 Kontak & Support

- **Author**: [Bertram Rayhan](https://bertramrayhan.vercel.app)
- **GitHub**: [@bertramrayhan](https://github.com/bertramrayhan)
- **Project Link**: [https://github.com/bertramrayhan/Jangkau](https://github.com/bertramrayhan/Jangkau)

### Laporkan Bug atau Request Fitur
Gunakan [GitHub Issues](https://github.com/bertramrayhan/Jangkau/issues) untuk melaporkan bug atau meminta fitur baru.

---

<p align="center">
  Made with ❤️ for Indonesian students
  <br>
  <strong>Jangkau - Temukan Peluang Prestasimu Berikutnya</strong>
</p>