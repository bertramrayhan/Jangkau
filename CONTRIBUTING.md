# Kontribusi ke Jangkau 🤝

Halo! Senang banget kamu mau ikut berkontribusi ke Jangkau! 🎉

Project ini masih kecil dan sedang berkembang, jadi semua bantuan dari teman-teman mahasiswa Indonesia sangat berarti.

## 🚀 Cara Mulai Kontribusi

### 1. Fork & Clone
```bash
# Fork dulu repository-nya di GitHub
# Terus clone ke komputer kamu
git clone https://github.com/[username-kamu]/Jangkau.git
cd Jangkau
```

### 2. Setup Project
```bash
# Bikin virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau venv\Scripts\activate di Windows

# Install dependencies
pip install -r requirements.txt
pip install -r webapp/requirements.txt
npm install

# Setup database
cd database && python init_db.py && cd ..

# Copy environment variables
cp .env.example .env
# Edit .env-nya sesuai kebutuhan
```

### 3. Jalankan Project
```bash
# Terminal 1: CSS
npm run dev

# Terminal 2: Flask App
cd webapp && python app.py

# Buka http://localhost:5000
```

### 4. Mulai Coding!
```bash
# Bikin branch baru
git checkout -b fitur-keren-ku

# Coding... coding... coding...
# Test dulu ya pastikan jalan

# Commit & push
git add .
git commit -m "feat: tambah fitur keren"
git push origin fitur-keren-ku

# Bikin Pull Request di GitHub
```

## 🎯 Apa Aja Yang Bisa Dikontribusi?

### 🐛 Nemu Bug?
Bikin issue aja, ceritain:
- Bug-nya apa
- Gimana cara reproduce-nya  
- Browser/OS apa yang kamu pakai

### 💡 Punya Ide Fitur?
Diskusi dulu di Issues! Kasih tau:
- Fitur apa yang kamu mau
- Kenapa fitur ini berguna
- Gimana cara kerjanya

### 💻 Mau Coding?
Bisa bantu di:
- **Frontend**: Improve UI/UX pakai TailwindCSS
- **Backend**: Tambahin fitur baru di Flask
- **Scraper**: Bantu improve atau tambahin sumber lomba baru
- **Database**: Optimize query atau tambahin field baru

### 📚 Documentation
- Improve README atau docs lainnya
- Tambahin komentar di code yang susah dimengerti
- Bikin tutorial atau guide

### 🌐 Sumber Website Lomba
Ini kontribusi yang super penting! Bantu kasih saran website sumber lomba yang bagus:
- **Universitas**: Website lomba dari kampus-kampus ternama
- **Organisasi**: Komunitas tech, bisnis, atau akademik  
- **Platform Lomba**: Situs khusus yang sering ngadain kompetisi
- **Media**: Portal berita yang sering publish info lomba

Caranya:
1. Bikin issue dengan judul: "Saran Sumber: [Nama Website]"
2. Kasih info: URL, jenis lomba yang sering ada, seberapa sering update
3. Kalau bisa, kasih contoh lomba yang pernah ada di sana

## 🤏 Aturan Simple

### Commit Messages
Pakai format simple aja:
```bash
feat: tambahin fitur search
fix: perbaiki bug pagination  
docs: update README
style: improve mobile UI
```

### Code Style
- **Python**: Pakai type hints kalau bisa, docstring untuk fungsi penting
- **HTML**: Semantic HTML + TailwindCSS
- **JavaScript**: Keep it simple, prioritas HTMX

### Testing
- Test manual dulu sebelum submit PR
- Pastikan app jalan di browser utama (Chrome, Firefox, Safari)
- Kalau ngubah scraper, test di beberapa website

## 🔧 Troubleshooting

**Database error?**
```bash
cd database && rm jangkau.db && python init_db.py
```

**CSS nggak update?**
```bash
npm run build
# Hard refresh browser (Ctrl+Shift+R)
```

**Port 5000 udah dipake?**
```bash
lsof -ti:5000 | xargs kill -9
```

## 💬 Butuh Bantuan?

- **GitHub Issues** - Untuk bug dan ide fitur
- **GitHub Discussions** - Untuk chat santai dan tanya-tanya

## 🙏 Thanks!

Project ini dibuat untuk membantu sesama mahasiswa Indonesia menemukan lomba dan beasiswa. Setiap kontribusi kamu, sekecil apapun, sangat berarti!

Let's build something awesome together! 🚀

---

<p align="center">
  <em>Made with ❤️ by Indonesian students, for Indonesian students</em>
</p>
