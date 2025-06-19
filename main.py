import os
from dotenv import load_dotenv

# Import untuk Pencarian dari Fase 2
from googleapiclient.discovery import build

# Import untuk LangChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain import hub # Untuk menarik prompt template

load_dotenv()


def cari_situs_terpercaya(query: str) -> list:
    """
    Fungsi untuk mencari query pada daftar situs terpercaya
    menggunakan Google Custom Search API.
    """
    api_key = os.getenv("GOOGLE_API_KEY_SEARCH")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        hasil = service.cse().list(q=query, cx=cse_id, num=5).execute()
       
        formatted_results = []
        if 'items' in hasil:
            for item in hasil.get('items', []):
                formatted_results.append({
                    "title": item.get('title'),
                    "link": item.get('link'),
                    "snippet": item.get('snippet')
                })
        return formatted_results
    except Exception as e:
        return [f"Terjadi error saat pencarian: {e}"]


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)


tools = [
    Tool(
        name="pencari_fakta_medis",
        func=cari_situs_terpercaya,
        description="Gunakan tool ini ketika kamu perlu mencari informasi medis atau kesehatan terkini dari sumber-sumber terpercaya di internet. Masukkan query pencarian yang relevan sebagai input."
    )
]

prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


print("="*50)
print("🩺 Selamat Datang di Asisten Cek Fakta Medis! 🩺")
print("Ketik 'keluar' untuk mengakhiri program.")
print("="*50)

while True:
    user_query = input("\nSilakan masukkan pertanyaan atau klaim medis Anda: ")
    if user_query.lower() == 'keluar':
        print("Terima kasih telah menggunakan asisten ini. Sampai jumpa!")
        break
    
   
    result = agent_executor.invoke({
        "input": user_query
    })

    print("\nJawaban Asisten:")
    print(result['output'])