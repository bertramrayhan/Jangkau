# Jangkau

<p align="center">
  <!-- Kamu bisa membuat logo sederhana nanti dan meletakkan link gambarnya di sini -->
  <!-- <img src="URL_LOGO_JANGKAU" alt="Logo Jangkau" width="150"/> -->
</p>

<h3 align="center">Membantu Mahasiswa Indonesia Menjangkau Potensi.</h3>

<p align="center">
  Satu tempat untuk semua informasi kompetisi, beasiswa, dan kesempatan lainnya. Dibangun secara terbuka oleh dan untuk komunitas mahasiswa Indonesia.
</p>

<p align="center">
  <a href="https://github.com/bertramrayhan/Jangkau/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/bertramrayhan/Jangkau?style=flat-square" alt="License"/>
  </a>
  <img src="https://img.shields.io/github/stars/bertramrayhan/Jangkau?style=flat-square" alt="Stars"/>
  <img src="https://img.shields.io/github/forks/bertramrayhan/Jangkau?style=flat-square" alt="Forks"/>
</p>

---

## 🚩 Latar Belakang Masalah

Informasi mengenai kompetisi, beasiswa, dan kesempatan berharga lainnya untuk mahasiswa Indonesia seringkali tersebar di berbagai platform, tidak terstruktur, dan sulit untuk ditemukan. Akibatnya, banyak mahasiswa kehilangan kesempatan emas untuk mengembangkan diri dan berprestasi.

## 💡 Solusi Kami: Jangkau

**Jangkau** adalah sebuah proyek *open-source* yang bertujuan untuk menyelesaikan masalah ini dengan cara:

1.  **Mengumpulkan:** Secara otomatis menjelajahi internet untuk mengumpulkan informasi dari berbagai sumber menggunakan *web scraper* cerdas.
2.  **Menstrukturkan:** Memanfaatkan AI untuk memahami dan mengubah data yang tidak terstruktur menjadi format JSON yang rapi dan konsisten.
3.  **Menyajikan:** Menampilkan semua informasi tersebut dalam satu platform yang bersih, mudah dicari, dan mudah diakses oleh semua.

Proyek ini lahir dari keresahan pribadi dan dibangun dengan semangat kolaborasi untuk membantu sesama mahasiswa.

## 🛠️ Arsitektur & Teknologi

Proyek ini dikelola sebagai **monorepo** (semua kode dalam satu repositori ) dan terdiri dari dua komponen utama:

*   `📁 /scraper/`: Kumpulan skrip yang bertugas untuk mengambil data.
    *   **Teknologi:** Python, Requests, BeautifulSoup, Playwright, Google Gemini API.
*   `📁 /web/`: Aplikasi web yang akan menampilkan data kepada pengguna.
    *   **Teknologi:** *Akan ditentukan kemudian.*

## 🚀 Peta Jalan (Roadmap)

Ini adalah proyek jangka panjang. Berikut adalah rencana pengembangan:

-   [ ] **Fase 1: Bukti Konsep (Proof of Concept)** - Membangun *scraper* pertama dan alur data inti untuk membuktikan ide ini bekerja.
-   [ ] **Fase 2: Peluncuran MVP (Minimum Viable Product)** - Meluncurkan website versi pertama dengan data dari beberapa sumber pilihan.
-   [ ] **Fase 3: Peningkatan Scraper** - Menambahkan dukungan untuk situs berbasis JavaScript dan optimasi deteksi konten baru menggunakan *hash*.
-   [ ] **Fase 4: Ekspansi Konten** - Mulai mengumpulkan data beasiswa dan kesempatan lainnya.

## 🤝 Ayo Berkontribusi!

Proyek ini tidak akan berhasil tanpa bantuan komunitas. Kamu bisa berkontribusi dengan berbagai cara, bahkan jika kamu bukan seorang *programmer*!

*   **Sumbang Ide:** Punya ide fitur atau tahu sumber informasi lomba yang bagus? Buat diskusi baru di tab **Issues**.
*   **Lapor Bug:** Menemukan masalah pada data atau website? Laporkan di **Issues**.
*   **Tulis Kode:** Ingin membantu mengembangkan? Cek panduan kontribusi kami (segera hadir) dan lihat daftar *Issues* yang bisa dikerjakan.

---

*Catatan: Proyek ini masih dalam tahap perencanaan awal. Kode pertama akan segera hadir setelah masa ujian berakhir!*