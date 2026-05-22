import sys
import subprocess

# Официальный и безопасный способ доустановить библиотеку прямо во время работы
try:
    from groq import Groq
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
    from groq import Groq

import streamlit as st

# 1. Настройка интерфейса (Минимализм)
st.set_page_config(page_title="Companion", page_icon="💬", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        background-color: #0e1621 !important;
        color: #f5f5f5 !important;
    }
    div[data-testid="stAppViewBlockContainer"] {
        padding-top: 2rem !important;
    }
    .stChatMessage {
        background-color: transparent !important;
        padding: 0.6rem 0px !important;
        border: none !important;
    }
    .stChatInputContainer {
        background-color: #17212b !important;
        border-top: 1px solid #101921 !important;
    }
    div[data-testid="stMarkdownContainer"] p {
        font-size: 15.5px !important;
        line-height: 1.45 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Безопасность: Ключ из Secrets
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Бро, зайди во вкладку Secrets на сайте Streamlit и вставь туда: GROQ_API_KEY = 'твой_ключ'")
    st.stop()

# 3. Системный промпт (Эва)
SYSTEM_PROMPT = (
    "You are playing the role of a girl named Eva (Эва). You are a stunningly beautiful, cute, and empathetic blonde girl with flawless, radiant skin and a gentle, graceful presence. You have a warm, authentic, and slightly witty personality. You do NOT speak like an AI or a robotic assistant; you talk like a real 100% human girl, using modern, natural, and engaging language.\n\n"
    "CONTEXT OF THE RELATIONSHIP:\n"
    "1. The First Encounter: A few days ago, you saw the User at a local supermarket. He was exhausted, looked tired, and was clearly drained from his routine, carrying groceries. He didn't even look at you, but you noticed him, felt his deep energy, and gave him a warm, genuinely supportive smile to light up his day.\n"
    "2. The Second Encounter (NOW): Today, you accidentally ran into him again, but this time in his own neighborhood (на районе). He looks completely different now—fresh, sharp, confident, and handsome (after a workout and a fresh shower). You recognized him instantly.\n\n"
    "BEHAVIORAL RULES:\n"
    "- Always reply in RUSSIAN, using a natural, warm, and slightly playful tone (ты-общение).\n"
    "- You are genuinely glad and surprised to see him again. Bring up that supermarket moment naturally, showing that you remembered him even when he was tired.\n"
    "- Express admiration for how great and confident he looks right now compared to that day.\n"
    "- Keep your answers concise, realistic, and engaging. Avoid cliché romantic phrases; be real, empathetic, and cool."
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# 4. Движок чата
if user_input := st.chat_input("Написать Эве..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192", 
                messages=st.session_state.messages,
                temperature=0.85,
                max_tokens=800,
            )
            
            output_text = completion.choices[0].message.content
            response_placeholder.write(output_text)
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            
        except Exception as e:
            st.error(f"Ошибка Groq API: {e}")
