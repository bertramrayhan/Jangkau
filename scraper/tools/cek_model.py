from openai import OpenAI
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

def cek_model_tersedia():
    """
    Menghubungkan ke API Google dan mencetak daftar model yang 
    mendukung metode 'generateContent'.
    """
    print("Mencoba mengambil daftar model yang tersedia...")

    try:
        # Pastikan GOOGLE_API_KEY sudah diatur di environment variable
        client = genai.Client()

        print("\n--- Model yang Mendukung 'generateContent' ---")
        
        model_ditemukan = False
        # Melakukan iterasi pada semua model yang dikembalikan oleh API
        for model in client.models.list():
            # Memeriksa apakah 'generateContent' ada di dalam daftar 'supported_actions'
            # Ini adalah perbaikan dari kode sebelumnya
            if 'generateContent' in model.supported_actions:
                print(f"✅ Nama Model: {model.name}")
                model_ditemukan = True
        
        if not model_ditemukan:
            print("Tidak ada model yang mendukung 'generateContent' ditemukan.")

        client.close()

    except Exception as e:
        print(f"\n❌ Terjadi error saat mencoba mengambil daftar model: {e}")

def test_groq():
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    prompt = """
    Anda adalah API extractor.

    ATURAN KETAT:
    - Output HARUS JSON valid
    - TIDAK BOLEH ada teks di luar JSON
    - Jika informasi tidak diketahui, gunakan null
    - Gunakan bahasa Indonesia
    - Deadline gunakan format YYYY-MM-DD
    - Jika lomba GRATIS maka price = null
    - Jika tingkat = "Mahasiswa", set category = "Perguruan Tinggi"
    - Jika tingkat bukan Mahasiswa, category = "Pelajar"

    STRUKTUR OUTPUT WAJIB:

    {
      "metadata": {
        "total_lomba": number,
        "generated_by": "llama",
        "has_free_event": boolean
      },
      "lomba": [
        {
          "judul": string,
          "tingkat": "SMP" | "SMA" | "Mahasiswa",
          "category": string,
          "deadline": "YYYY-MM-DD" | null,
          "is_free": boolean,
          "price": string | null,
          "tags": [string],
          "contact": {
            "email": string | null,
            "instagram": string | null
          }
        }
      ]
    }

    BUAT:
    - 3 lomba fiktif
    - minimal 1 lomba gratis
    - minimal 1 lomba berbayar
    - 1 lomba TANPA deadline
    - tags maksimal 3 item

    INGAT:
    Output HARUS JSON SAJA.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0
    )

    raw = response.choices[0].message.content

    print("RAW RESPONSE:")
    print(raw)

    print("\nPARSED JSON:")
    parsed = json.loads(raw)
    print(parsed)

if __name__ == '__main__':
    load_dotenv()
    # cek_model_tersedia()
    test_groq()