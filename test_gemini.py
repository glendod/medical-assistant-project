import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

print("Mencoba mengkonfigurasi API...")
try:
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    print("Konfigurasi API berhasil.")
except Exception as e:
    print(f"Error saat konfigurasi: {e}")
    exit()


model = genai.GenerativeModel('gemini-2.5-flash') 

print(f"\nModel yang digunakan: {model.model_name}")


prompt = "Jelaskan secara sederhana dalam bahasa Indonesia, apa itu hormon kortisol dan apa fungsinya?"

print(f"Mengirim prompt: '{prompt}'")
print("--------------------------------------------------")


response = model.generate_content(prompt)

print("Respons dari Gemini:")
print(response.text)