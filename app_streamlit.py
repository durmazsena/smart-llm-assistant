import streamlit as st
import requests
import uuid

# API URL
SMART_API_URL = "http://localhost:8000/smart_chat"
RAG_UPLOAD_URL = "http://localhost:8000/rag/upload"

# Page config
st.set_page_config(
    page_title="Smart LLM Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Light Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Force Light Theme */
    .stApp, .main, [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #ffffff 0%, #fff8f3 50%, #fff0e6 100%) !important;
    }
    
    #MainMenu, footer, header, [data-testid="stHeader"] {
        visibility: hidden !important;
        display: none !important;
    }
    
    .main .block-container {
        padding: 2rem 3rem !important;
        max-width: 900px !important;
        margin: 0 auto !important;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .sub-header {
        color: #4a5568;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.25) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(255, 107, 53, 0.35) !important;
    }
    
    /* Chat Input */
    [data-testid="stChatInput"] {
        background: #ffffff !important;
        border: 2px solid rgba(255, 107, 53, 0.2) !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 20px rgba(255, 107, 53, 0.1) !important;
    }
    
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #2d3748 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%) !important;
        border-radius: 12px !important;
    }
    
    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background: #ffffff !important;
        border-radius: 20px !important;
        padding: 1.25rem !important;
        margin-bottom: 1rem !important;
        border: 1px solid rgba(255, 107, 53, 0.1) !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04) !important;
    }
    
    [data-testid="stChatMessage"] p {
        color: #2d3748 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Mode badges */
    .mode-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        font-family: 'Inter', sans-serif;
    }
    
    .mode-chat {
        background: rgba(255, 107, 53, 0.12);
        color: #ff6b35;
        border: 1px solid rgba(255, 107, 53, 0.2);
    }
    
    .mode-web {
        background: rgba(66, 153, 225, 0.12);
        color: #3182ce;
        border: 1px solid rgba(66, 153, 225, 0.2);
    }
    
    .mode-rag {
        background: rgba(72, 187, 120, 0.12);
        color: #38a169;
        border: 1px solid rgba(72, 187, 120, 0.2);
    }
    
    /* File indicator */
    .file-indicator {
        background: rgba(72, 187, 120, 0.08);
        border: 1px solid rgba(72, 187, 120, 0.2);
        color: #38a169;
        padding: 0.75rem 1.25rem;
        border-radius: 14px;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Settings box */
    .settings-box {
        background: #ffffff;
        border: 1px solid rgba(255, 107, 53, 0.15);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .settings-title {
        color: #4a5568;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: transparent !important;
        padding: 0 !important;
        border: none !important;
    }
    
    .stRadio label, .stRadio p {
        color: #4a5568 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #ffffff !important;
        border: 2px dashed #ff6b35 !important;
        border-radius: 18px !important;
        padding: 2rem !important;
    }
    
    /* Divider */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255, 107, 53, 0.2), transparent) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Text */
    p, span, label {
        color: #2d3748 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Code */
    .stMarkdown code {
        background: #fff0e6 !important;
        color: #ff6b35 !important;
        padding: 0.2rem 0.5rem !important;
        border-radius: 6px !important;
    }
    
    .stMarkdown pre {
        background: #2d3748 !important;
        border-radius: 14px !important;
    }
    
    /* Links */
    a { color: #ff6b35 !important; }
    
    /* Footer */
    .footer-text {
        text-align: center;
        margin-top: 3rem;
        color: #718096;
        font-size: 0.85rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Modal */
    [data-testid="stModal"] > div {
        background: #ffffff !important;
        border-radius: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state - proper initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "force_mode" not in st.session_state:
    st.session_state.force_mode = None
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

# File upload dialog - separate function
@st.dialog("📁 Dosya Yükle")
def show_upload_dialog():
    st.markdown("**Desteklenen formatlar:** PDF, TXT, DOCX")
    
    uploaded_file = st.file_uploader(
        "Dosyayı sürükleyin veya seçin",
        type=["pdf", "txt", "docx"],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        with st.spinner("📤 Dosya işleniyor..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post(
                f"{RAG_UPLOAD_URL}?session_id={st.session_state.session_id}",
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.uploaded_file_name = uploaded_file.name
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"✅ **{uploaded_file.name}** başarıyla yüklendi! ({result['chunks']} chunk)",
                    "mode": "rag"
                })
                st.rerun()
            else:
                st.error("❌ Dosya yüklenirken hata oluştu!")
    
    if st.button("❌ Kapat", use_container_width=True):
        st.rerun()

# Header
st.markdown('<h1 class="main-header">🧠 Smart LLM Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Akıllı yönlendirmeli yazılım mimarı asistanı</p>', unsafe_allow_html=True)

# Top bar - separate button handling
col1, col2, col3 = st.columns([1, 6, 1])

with col1:
    upload_btn = st.button("📎", help="Dosya Yükle", use_container_width=True, key="upload_btn")

with col3:
    settings_btn = st.button("⚙️", help="Ayarlar", use_container_width=True, key="settings_btn")

# Handle button clicks separately
if upload_btn:
    show_upload_dialog()

if settings_btn:
    st.session_state.show_settings = not st.session_state.show_settings
    st.rerun()

# File indicator
if st.session_state.uploaded_file_name:
    st.markdown(f'''
    <div class="file-indicator">
        📄 <strong>{st.session_state.uploaded_file_name}</strong>
    </div>
    ''', unsafe_allow_html=True)

# Settings - using custom HTML instead of expander
if st.session_state.show_settings:
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    st.markdown('<p class="settings-title">⚙️ Mod Ayarları</p>', unsafe_allow_html=True)
    
    mode_options = {
        "🤖 Otomatik": None,
        "💬 Chat": "chat",
        "🌐 Web Search": "web_search",
        "📄 RAG": "rag"
    }
    selected = st.radio(
        "Yanıt modu:",
        options=list(mode_options.keys()),
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.force_mode = mode_options[selected]
    
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Mode badge helper
def get_mode_badge(mode):
    return {
        "chat": '<span class="mode-badge mode-chat">💬 Chat</span>',
        "web_search": '<span class="mode-badge mode-web">🌐 Web</span>',
        "rag": '<span class="mode-badge mode-rag">📄 RAG</span>'
    }.get(mode, "")

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧠" if msg["role"] == "assistant" else "👤"):
        if msg["role"] == "assistant" and "mode" in msg:
            st.markdown(get_mode_badge(msg["mode"]), unsafe_allow_html=True)
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Mesajınızı yazın...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    payload = {
        "session_id": st.session_state.session_id,
        "message": user_input,
        "force_mode": st.session_state.force_mode
    }
    
    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner(""):
            try:
                response = requests.post(SMART_API_URL, json=payload, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    mode = result["mode_used"]
                    answer = result["answer"]
                    
                    st.markdown(get_mode_badge(mode), unsafe_allow_html=True)
                    st.markdown(answer)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "mode": mode
                    })
                else:
                    st.error(f"❌ API hatası: {response.status_code}")
            except requests.exceptions.Timeout:
                st.error("⏱️ Zaman aşımı")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Bağlantı hatası")
            except Exception as e:
                st.error(f"❌ Hata: {str(e)}")

# Footer
st.markdown('<p class="footer-text">Powered by Ollama + LangChain + Semantic Router</p>', unsafe_allow_html=True)