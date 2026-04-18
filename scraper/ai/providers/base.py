from abc import ABC, abstractmethod
from config.logging_config import logger


class BaseAIProvider(ABC):
    """
    Abstract base class untuk semua AI provider.
    
    Setiap provider (Gemini, Groq, dll) harus implement:
    - model_list: List model yang tersedia untuk provider
    - strukturkan_dengan_ai(): Method untuk process batch data
    """
    
    MAX_RETRIES_PER_MODEL = 5  # Max retry per model sebelum switch
    BASE_DELAY = 5  # Base delay untuk exponential backoff (detik)

    def __init__(self):
        """Initialize provider dengan default state."""
        self.is_limit = False  # Flag untuk track apakah provider reach limit
    
    @property
    @abstractmethod
    def model_list(self):
        """
        Setiap AI provider memberikan list AI model yang bisa digunakan.
        
        Returns:
            list: List nama model yang tersedia
        """
        pass

    @abstractmethod
    def strukturkan_dengan_ai(self, valid_tags, batch_lomba_mentah):
        """
        Main method untuk proses batch data menggunakan AI.
        
        Args:
            valid_tags (list): List tag yang valid untuk classification
            batch_lomba_mentah (list): Batch data lomba yang akan diproses
        
        Returns:
            list: Array JSON hasil proses, atau None jika gagal/exhausted
        
        Raises:
            Exception: Jika ada error unexpected
        """
        pass

    def get_batch_prompt(self, valid_tags, batch_lomba_mentah):
        """
        Generate prompt untuk AI provider.
        
        Args:
            valid_tags (list): List tag yang valid untuk classification
            batch_lomba_mentah (list): Batch data lomba
        
        Returns:
            str: Formatted prompt untuk AI
        
        Raises:
            ValueError: Jika ada parameter yang tidak valid
        """
        # Validasi input
        if not valid_tags:
            logger.warning("⚠️ valid_tags kosong, mungkin ekstraksi tag tidak optimal")
            valid_tags = []
        
        if not batch_lomba_mentah:
            raise ValueError("batch_lomba_mentah tidak boleh kosong")
        
        # Validasi setiap item dalam batch
        required_fields = ['source_url', 'title', 'content_html']
        for idx, item in enumerate(batch_lomba_mentah):
            for field in required_fields:
                if field not in item:
                    raise ValueError(
                        f"Item {idx} kehilangan field wajib '{field}'. "
                        f"Batch items harus memiliki: {required_fields}"
                    )
                if item[field] is None:
                    raise ValueError(
                        f"Item {idx} memiliki field '{field}' bernilai None. "
                        f"Field wajib tidak boleh None."
                    )
        
        # Build batch text input
        batch_text_input = ""
        for lomba_mentah in batch_lomba_mentah:
            batch_text_input += f'''
            SOURCE_URL: {lomba_mentah['source_url']}
            TITLE: {lomba_mentah['title']}
            CONTENT_HTML:
            """
            {lomba_mentah['content_html']}
            """

            --- ITEM BARU ---

            '''

        return f'''
        PERAN:
        Anda adalah sebuah API pemrosesan batch yang sangat akurat. Tugas Anda adalah menerima serangkaian data mentah berisi HTML, dan mengembalikan sebuah ARRAY JSON yang berisi hasil pemrosesan lengkap untuk SETIAP item.

        TUGAS UTAMA (berlaku untuk setiap item input):
        Lakukan proses dua langkah berikut secara internal:
        1.  **LANGKAH 1: ANALISIS & PEMBERSIHAN HTML**
            *   Ambil `CONTENT_HTML` mentah.
            *   Hapus semua elemen "sampah" seperti `<script>`, `<style>`, iklan, `<div>` yang tidak perlu, dan atribut `style="..."` atau `class="..."`.
            *   Dari HTML yang sudah dianalisis ini, buatlah versi `clean_html` yang siap ditampilkan, hanya menggunakan tag semantik seperti `<h2>`, `<h3>`, `<p>`, `<ul>`, `<li>`, `<strong>`, dan `<a>`.
        2.  **LANGKAH 2: EKSTRAKSI INFORMASI**
            *   Berdasarkan pemahaman Anda dari konten di Langkah 1, ekstrak semua informasi kunci lainnya sesuai ATURAN EKSTRAKSI di bawah.

        ATURAN EKSTRAKSI (berlaku untuk Langkah 2):
        1.  **`title`**: WAJIB diisi dengan judul yang tertera di input untuk setiap lomba.
        2.  **Format Tanggal**: Gunakan format `YYYY-MM-DD`. Jika tahun tidak ada, asumsikan `2025` atau `2026` berdasarkan konteks. Jika tidak ada info tanggal, gunakan `null`.
        3.  **`is_free`**: Gunakan `true` jika teks menyebut 'GRATIS'/'FREE'. Gunakan `false` jika ada harga. Gunakan `null` jika tidak ada info biaya.
        4.  **`tags`**: Pilih beberapa tag yang paling relevan HANYA dari daftar berikut: [{valid_tags}].
        5.  **`registration_link`**: Prioritaskan link dari platform seperti 'linktr.ee', 'bit.ly', atau yang mengandung kata 'daftar'/'register'. Jika tidak ada, gunakan `null`.
        6.  **Nilai `null`**: Untuk field lain, jika informasinya tidak dapat ditemukan, WAJIB gunakan nilai `null`.
        7.  **`price_details`**: Jika `is_free` true maka price_details null. Jika tidak tertera adanya biaya pendaftaran, maka isilah dengan null.

        STRUKTUR WAJIB UNTUK SETIAP OBJEK JSON:
        {{
        "title": "string",
        "source_url": "salin url pada lomba",
        "content_html": "HTML bersih dari LANGKAH 1.",
        "organizer": "string atau null",
        "registration_start": "YYYY-MM-DD atau null",
        "registration_end": "YYYY-MM-DD atau null",
        "event_start": "YYYY-MM-DD atau null",
        "event_end": "YYYY-MM-DD atau null",
        "is_free": boolean atau null,
        "price_details": "string atau null",
        "location": "string ('Online', 'Offline', 'Hybrid') atau null",
        "location_details": "string atau null",
        "tags": ["array", "of", "strings"],
        "registration_link": "string (URL) atau null"
        }}

        INPUT:
        Serangkaian data acara di bawah ini. Setiap acara dipisahkan oleh "--- LOMBA BARU ---".
        ---
        {batch_text_input}
        ---

        ATURAN OUTPUT FINAL:
        Respons Anda HARUS HANYA berisi array JSON `[...]` yang valid. Jangan sertakan teks pembuka, penutup, markdown (```json), atau penjelasan apa pun.
        '''