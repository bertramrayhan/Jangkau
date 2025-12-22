# File: scraper/cek_model.py

import os
from google import genai
from google.genai import types

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
        for model in client.models.list()[:5]:
            # Memeriksa apakah 'generateContent' ada di dalam daftar 'supported_actions'
            # Ini adalah perbaikan dari kode sebelumnya
            print(model)
            if 'generateContent' in model.supported_actions:
                print(f"✅ Nama Model: {model.name}")
                model_ditemukan = True
        
        if not model_ditemukan:
            print("Tidak ada model yang mendukung 'generateContent' ditemukan.")

        client.close()

    except Exception as e:
        print(f"\n❌ Terjadi error saat mencoba mengambil daftar model: {e}")

if __name__ == '__main__':
    cek_model_tersedia()