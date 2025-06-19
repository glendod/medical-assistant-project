import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()


api_key = os.getenv("GOOGLE_API_KEY_SEARCH")
cse_id = os.getenv("GOOGLE_CSE_ID")

def cari_situs_terpercaya(query, jumlah_hasil=5):
    """
    Fungsi untuk mencari query pada daftar situs terpercaya
    menggunakan Google Custom Search API.
    """
    try:
       
        service = build("customsearch", "v1", developerKey=api_key)
        
       
        hasil = service.cse().list(
            q=query,      # Query pencarian
            cx=cse_id,    # Search Engine ID 
            num=jumlah_hasil  # Jumlah hasil yang diinginkan
        ).execute()

        # Kembalikan daftar hasil pencarian
        return hasil.get('items', [])

    except Exception as e:
        print(f"Terjadi error saat pencarian: {e}")
        return []


if __name__ == "__main__":
    # Contoh query yang akan kita cari
    contoh_query = "efek samping begadang bagi kesehatan"
    print(f"Melakukan pencarian untuk: '{contoh_query}'\n")

    # Panggil fungsi pencarian
    hasil_pencarian = cari_situs_terpercaya(contoh_query)

    # Periksa dan cetak hasilnya
    if not hasil_pencarian:
        print("Tidak ada hasil yang ditemukan atau terjadi error.")
    else:
        print(f"Menemukan {len(hasil_pencarian)} hasil:\n")
        # Loop melalui setiap hasil dan cetak informasinya
        for i, item in enumerate(hasil_pencarian):
            print(f"--- Hasil #{i+1} ---")
            print(f"Judul: {item['title']}")
            print(f"Link: {item['link']}")
            print(f"Kutipan: {item['snippet']}")
            print("-" * 20)