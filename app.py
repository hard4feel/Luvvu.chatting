import streamlit as st
from groq import Groq

# 1. Настройка страницы в стиле Тотал-Блэк / Минимализм
st.set_page_config(page_title="Companion", page_icon="💬", layout="centered")

# Чистим интерфейс от стандартных плашек Streamlit, оставляем только чистый экран
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stAppViewBlockContainer"] {
        padding-top: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Секретный ввод токена (Скрывает символы точками)
if "GROQ_API_KEY" in st.secrets:
    groq_key = st.secrets["GROQ_API_KEY"]
else:
    groq_key = st.text_input("Введи Groq API Key для авторизации:", type="password")
    st.markdown("---")

# 3. Системный промпт (Логика Эвы)
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

# Инициализация истории чата
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Рендерим только диалог, без системных инструкций
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# 4. Рабочий движок чата (Groq LPU)
if user_input := st.chat_input("Написать Эве..."):
    if not groq_key:
        st.error("Ошибка: Сначaла введи свой секретный ключ!")
    else:
        # Инициализация клиента напрямую
        client = Groq(api_key=groq_key)
        
        # Запись и вывод сообщения юзера
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        # Генерация ответа от Эвы
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            try:
                completion = client.chat.completions.create(
                    model="llama3-70b-8192",  # Мощная модель, которая вывезит контекст
                    messages=st.session_state.messages,
                    temperature=0.85,         # Добавили чуть больше живости в общение
                    max_tokens=800,
                )
                
                output_text = completion.choices[0].message.content
                response_placeholder.write(output_text)
                
                st.session_state.messages.append({"role": "assistant", "content": output_text})
                
            except Exception as e:
                st.error(f"Ошибка API: {e}")
