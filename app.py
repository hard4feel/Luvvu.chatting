import streamlit as st
from groq import Groq

# 1. Настройка страницы под любые экраны (ПК и мобилки)
st.set_page_config(
    page_title="Companion Chat", 
    page_icon="💬", 
    layout="centered"  # Центрируем контент, чтобы на ПК текст не расползался
)

# 2. Адаптивный Telegram-Style дизайн (Интерфейс мессенджера)
st.markdown("""
    <style>
    /* Отключаем дефолтные элементы интерфейса Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Тотальный темный фон как в ТГ */
    .stApp {
        background-color: #0e1621 !important;
        color: #f5f5f5 !important;
    }
    
    /* Ограничиваем максимальную ширину чата, чтобы на ПК смотрелось аккуратно */
    div[data-testid="stAppViewBlockContainer"] {
        max-width: 650px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 5rem !important;
    }
    
    /* Кастомные контейнеры для выравнивания сообщений */
    .chat-row {
        display: flex;
        margin-bottom: 12px;
        width: 100%;
    }
    .chat-row.user-row {
        justify-content: flex-end; /* Твои сообщения — справа */
    }
    .chat-row.eva-row {
        justify-content: flex-start; /* Ответы Эвы — слева */
    }
    
    /* Пузыри сообщений */
    .chat-bubble {
        padding: 10px 14px;
        border-radius: 16px;
        max-width: 85%; /* Ограничение ширины для экранов телефонов */
        font-size: 15px;
        line-height: 1.4;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .user-bubble {
        background-color: #2b5278 !important; /* Синий цвет сообщений юзера */
        color: #ffffff !important;
        border-bottom-right-radius: 4px; /* Скос угла */
    }
    .eva-bubble {
        background-color: #182533 !important; /* Темно-серый для Эвы */
        color: #f5f5f5 !important;
        border-bottom-left-radius: 4px;
    }
    
    /* Стилизация нижнего поля ввода сообщения */
    .stChatInputContainer {
        background-color: #17212b !important;
        border-top: 1px solid #101921 !important;
        padding-bottom: 20px !important;
    }
    .stChatInputContainer textarea {
        background-color: #24303f !important;
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Безопасность: Подтягиваем ключ из вкладки Secrets на сайте Streamlit
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Бро, зайди во вкладку Secrets на сайте Streamlit и вставь туда строку: GROQ_API_KEY = 'твой_ключ'")
    st.stop()

# 4. Прошивка Эвы (Системный промпт)
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

# Инициализируем память диалога
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Отрисовка истории переписки в кастомном стиле
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-row user-row"><div class="chat-bubble user-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="chat-row eva-row"><div class="chat-bubble eva-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)

# 5. Логика отправки сообщений на Groq LPU
if user_input := st.chat_input("Написать Эве..."):
    # Сохраняем сообщение пользователя и выводим его на экран
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f'<div class="chat-row user-row"><div class="chat-bubble user-bubble">{user_input}</div></div>', unsafe_allow_html=True)
    
    # Отправляем всю историю на генерацию модели Llama 3
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192", 
            messages=st.session_state.messages,
            temperature=0.85,
            max_tokens=800,
        )
        
        output_text = completion.choices[0].message.content
        
        # Сохраняем ответ бота в память
        st.session_state.messages.append({"role": "assistant", "content": output_text})
        
        # Перезагружаем страницу, чтобы обновить UI без дублирования блоков
        st.rerun()
        
    except Exception as e:
        st.error(f"Ошибка Groq API: {e}")