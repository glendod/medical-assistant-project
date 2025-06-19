# 1. Imports
# -----------------------------------------------------------------------------
import os
import streamlit as st
from dotenv import load_dotenv

# Import untuk Pencarian
from googleapiclient.discovery import build

# Import untuk LangChain (dengan tambahan untuk memori)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage


# 2. Fungsi dan Setup Agent
# -----------------------------------------------------------------------------
load_dotenv()

# Fungsi pencarian yang sudah kita buat di Fase 2
def cari_situs_terpercaya(query: str) -> list:
    """Fungsi untuk mencari query pada daftar situs terpercaya."""
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

# Inisialisasi LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Membuat Tools
tools = [
    Tool(
        name="pencari_fakta_medis",
        func=cari_situs_terpercaya,
        description="Gunakan tool ini ketika kamu perlu mencari informasi medis atau kesehatan terkini dari sumber-sumber terpercaya di internet. Masukkan query pencarian yang relevan sebagai input."
    )
]

# Membuat Prompt Template Kustom yang mendukung riwayat percakapan
system_message = """
Assistant is a helper for questions about medical claims, providing answers from trusted sources.

TOOLS:
------
Assistant has access to the following tools:
{tools}

To use a tool, please use the following format:

Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

Thought: Do I need to use a tool? No
Final Answer: [the final answer to the original input question]

PENTING: Setelah memberikan jawaban akhir, kamu WAJIB menyertakan bagian "Referensi:" di bawah jawabanmu. Cantumkan daftar bernomor dari sumber-sumber yang kamu gunakan dari hasil `pencari_fakta_medis`, lengkap dengan judul dan link-nya. Jika kamu tidak menggunakan tool pencarian, sebutkan bahwa jawaban dihasilkan tanpa referensi eksternal.

Begin!
"""

# Membuat prompt dari template yang mendukung chat history
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])
prompt.input_variables.append("agent_scratchpad")


# Membuat Agent
agent = create_react_agent(llm, tools, prompt)

# Membuat Agent Executor dengan batasan iterasi dan untuk mengembalikan intermediate steps
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=3,
    return_intermediate_steps=True
)


# 3. Konfigurasi Halaman dan Aplikasi Streamlit
# -----------------------------------------------------------------------------

st.set_page_config(page_title="Asisten Cek Fakta Medis", page_icon="🩺")
st.title("🩺 Asisten Cek Fakta Medis")
st.markdown("Dibuat oleh **Glend Aldo Marcelino**")

# Inisialisasi "memory" untuk menyimpan riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Menampilkan riwayat chat yang sudah ada
for message in st.session_state.messages:
    with st.chat_message(message.type):
        st.markdown(message.content)

# Menerima input dari pengguna menggunakan chat_input
if user_query := st.chat_input("Tanyakan klaim medis atau pertanyaan kesehatan..."):
    st.session_state.messages.append(HumanMessage(content=user_query))
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("..."):
            response = agent_executor.invoke({
                "input": user_query,
                "chat_history": st.session_state.messages
            })

            final_answer = response['output']

            if "Agent stopped due to iteration limit" in final_answer:
                intermediate_steps = response.get("intermediate_steps", [])
                steps_text = "\n".join([str(step) for step in intermediate_steps])
                
                summary_prompt = f"""
                Berdasarkan pertanyaan pengguna: '{user_query}' dan langkah-langkah penelitian yang sudah kamu lakukan sejauh ini:
                ---
                {steps_text}
                ---
                Tolong berikan jawaban rangkuman terbaik yang bisa kamu berikan kepada pengguna.

                PENTING: Setelah memberikan jawaban rangkuman, kamu WAJIB menyertakan bagian "Referensi:" di bawah jawabanmu. Cantumkan daftar bernomor dari sumber-sumber yang kamu temukan dalam langkah-langkah penelitian di atas, lengkap dengan judul dan link-nya.
                """
                summary_response = llm.invoke(summary_prompt)
                final_answer = summary_response.content
            
            st.markdown(final_answer)

    st.session_state.messages.append(AIMessage(content=final_answer))