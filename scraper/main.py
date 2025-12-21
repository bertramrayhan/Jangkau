import requests
from bs4 import BeautifulSoup
import re
from google import genai
from google.genai import types
import json
import os

base_url = 'https://www.infolombait.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_prompt(title, description):
    return f"""
    PERAN: Anda adalah sebuah API. Tugas Anda adalah menerima teks deskripsi sebuah acara, dan mengembalikannya dalam format JSON yang ketat. Jangan memberikan penjelasan atau teks tambahan apa pun selain JSON itu sendiri.

    INPUT:
    Teks deskripsi acara dengan judul "{title}" adalah sebagai berikut:
    ---
    {description}
    ---

    TUGAS:
    Berdasarkan INPUT di atas, ekstrak informasi ke dalam struktur JSON di bawah.

    ATURAN EKSTRAKSI:
    1.  **Format Tanggal**: Gunakan format standar internasional `YYYY-MM-DD`. Jika tahun tidak ada, asumsikan `2025` atau `2026` berdasarkan konteks.
    2.  **Nilai `null`**: Jika suatu field tidak dapat ditemukan informasinya di dalam teks, WAJIB gunakan nilai `null`.
    3.  **Field `is_free`**: Gunakan `true` jika teks menyebut 'GRATIS'/'FREE'. Gunakan `false` jika ada harga. Gunakan `null` jika tidak ada info biaya.
    4.  **Field `tags`**: Pilih beberapa tag yang paling relevan dari daftar yang disediakan dalam contoh JSON.
    5.  **Field `registration_link`**: Prioritaskan link yang mengandung kata 'daftar', 'register', atau dari platform seperti 'linktr.ee' atau 'bit.ly'.

    CONTOH OUTPUT JSON (Struktur Wajib):
    {{
    "organizer": "string atau null",
    "registration_start": "YYYY-MM-DD atau null",
    "registration_end": "YYYY-MM-DD atau null",
    "event_start": "YYYY-MM-DD atau null",
    "event_end": "YYYY-MM-DD atau null",
    "is_free": boolean atau null,
    "price_details": "string atau null",
    "location": "string ('Online', 'Offline', 'Hybrid') atau null",
    "location_details": "string atau null",
    "tags": ["Programming", "Hackathon", "CTF", "Data Science", "UI/UX Design", "Desain Grafis", "Business Case", "Debat", "Menulis Esai", "Robotika", "Mahasiswa", "SMA", "Umum", "Gratis", "Berbayar", "Online", "Offline", "Hybrid"],
    "registration_link": "string (URL) atau null"
    }}
    """

def strukturkan_dengan_ai(data_lomba_mentah):
    print("\n--- Menghubungi AI untuk menstrukturkan data (Cara Terbaru)... ---")
    
    title = data_lomba_mentah.get('title', 'Tanpa Judul')
    description = data_lomba_mentah.get('description', '')
    
    prompt = get_prompt(title, description)
    
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

        response = client.models.generate_content(
            model='models/gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        
        data_terstruktur = json.loads(response.text)
        
        print("✅ AI berhasil menstrukturkan data.")
        client.close()
        return data_terstruktur
        
    except Exception as e:
        print(f"❌ Gagal saat berinteraksi dengan AI. Error: {e}")
        if 'response' in locals():
            print(f"   Prompt Feedback: {getattr(response, 'prompt_feedback', 'N/A')}")
            print(f"   Teks Mentah: {getattr(response, 'text', 'N/A')}")
        return None

def traverse_url(title, url):
    print(f"Mengambil deskripsi lomba dari satu halaman: {url}" )

    data_lomba = {
        'title': title,
        'url': url
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        deskripsi_lomba_scope = soup.select_one('div.entry-content')

        if deskripsi_lomba_scope:
            print(f"\n✅ Berhasil menemukan deskripsi lomba:")

            deskripsi_lomba_tags = deskripsi_lomba_scope.select('p')
            print(f"\n--- Memulai Investigasi {len(deskripsi_lomba_tags)} Paragraf ---")

            final_description_parts = []

            for i, p_tag in enumerate(deskripsi_lomba_tags):
                
                text = ''

                if not p_tag.get_text(strip=True):
                    final_description_parts.append('\n') 
                    continue
                else:
                    text = p_tag.get_text(strip=True)
                    final_description_parts.append(text)

                final_description_parts.append('\n') 

            deskripsi_lomba = ''.join(final_description_parts)

            deskripsi_lomba_bersih = re.sub(r'\n{3,}', '\n\n', deskripsi_lomba)

            data_lomba['description'] = deskripsi_lomba_bersih
            return data_lomba
        else:
            print("\n❌ Gagal menemukan deskripsi lomba dengan selector yang digunakan.")
            print("    Mungkin struktur HTML situs telah berubah. Perlu investigasi ulang.")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Gagal melakukan request ke URL. Error: {e}")
    except Exception as e:
        print(f"\n❌ Terjadi sebuah error: {e}")

def main():
    print(f"Mengambil daftar lomba dari halaman utama: {base_url}" )

    try:
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        list_lomba = soup.select('article')

        if list_lomba:
            print(f"\n✅ Berhasil menemukan {len(list_lomba)} lomba:")
            
            for lomba in list_lomba:
                lomba_url_tag = lomba.select_one('h2.entry-title a');

                lomba_title = lomba_url_tag.text.strip()
                lomba_url = lomba_url_tag['href'];

                print(f"  - Judul: {lomba_title}")
                print(f"    Link: {lomba_url}")

                dict_lomba = traverse_url(lomba_title, lomba_url)
                print('\n')
                print(strukturkan_dengan_ai(dict_lomba))
            
        else:
            print("\n❌ Gagal menemukan link lomba dengan selector yang digunakan.")
            print("    Mungkin struktur HTML situs telah berubah. Perlu investigasi ulang.")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Gagal melakukan request ke URL. Error: {e}")
    except Exception as e:
        print(f"\n❌ Terjadi sebuah error: {e}")

if __name__ == '__main__':
    main()