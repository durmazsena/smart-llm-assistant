import streamlit as st
import requests
import uuid

# API URL
SMART_API_URL = "http://localhost:8000/smart_chat"
RAG_UPLOAD_URL = "http://localhost:8000/rag/upload"

st.set_page_config(
    page_title="Yazılım Mimarı Asistanı",
    page_icon="🤖"
)

# Özel CSS
st.markdown("""
<style>
    /* Primary buton - yeşil */
    .stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        border-color: #28a745 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
    }
    
    /* File Uploader - Yeşil kesik çizgili stil */
    [data-testid="stFileUploader"] {
        border: 2px dashed #4CAF50 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        background-color: rgba(76, 175, 80, 0.05) !important;
    }
    [data-testid="stFileUploader"]:hover {
        background-color: rgba(76, 175, 80, 0.1) !important;
        border-color: #45a049 !important;
    }
    [data-testid="stFileUploader"] section > button {
        background-color: #4CAF50 !important;
        color: white !important;
        border: none !important;
    }
    
    /* Mode badge stilleri */
    .mode-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-bottom: 5px;
    }
    .mode-chat { background-color: #e3f2fd; color: #1976d2; }
    .mode-web { background-color: #fff3e0; color: #f57c00; }
    .mode-rag { background-color: #e8f5e9; color: #388e3c; }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

if "show_upload_dialog" not in st.session_state:
    st.session_state.show_upload_dialog = False

if "force_mode" not in st.session_state:
    st.session_state.force_mode = None  # None = otomatik

# Dosya yükleme dialog fonksiyonu
@st.dialog("📁 Dosya Yükle")
def upload_file_dialog():
    st.caption("📎 Dosyayı sürükleyip bırakın veya 'Browse files' butonuna tıklayın")
    
    uploaded_file = st.file_uploader(
        "PDF, TXT veya DOCX dosyası seçin",
        type=["pdf", "txt", "docx"],
        help="Desteklenen formatlar: PDF, TXT, DOCX"
    )
    
    if uploaded_file is not None:
        with st.spinner("Dosya işleniyor..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post(
                f"{RAG_UPLOAD_URL}?session_id={st.session_state.session_id}",
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.uploaded_file_name = uploaded_file.name
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"✅ **{uploaded_file.name}** başarıyla yüklendi! ({result['chunks']} chunk oluşturuldu)"
                    }
                )
                st.session_state.show_upload_dialog = False
                st.rerun()
            else:
                st.error("Dosya yüklenirken hata oluştu!")
    
    if st.button("❌ Kapat"):
        st.session_state.show_upload_dialog = False
        st.rerun()

# Header
col_title, col_upload = st.columns([5, 1])
with col_title:
    st.title("🤖 Yazılım Mimarı Asistanı")
with col_upload:
    st.write("")  # Hizalama için boşluk
    if st.button("📎 Dosya", use_container_width=True):
        st.session_state.show_upload_dialog = True

# Dialog göster
if st.session_state.show_upload_dialog:
    upload_file_dialog()

# Aktif dosya göstergesi
if st.session_state.uploaded_file_name:
    st.success(f"📄 Aktif dosya: **{st.session_state.uploaded_file_name}**")

st.caption("🧠 Akıllı mod: Asistan sorunuza göre en uygun kaynağı otomatik seçer")

# Override seçeneği (expander içinde)
with st.expander("⚙️ Mod Ayarları", expanded=False):
    mode_options = {
        "🤖 Otomatik": None,
        "💬 Sadece Chat": "chat",
        "🌐 Sadece Web Search": "web_search",
        "📄 Sadece RAG": "rag"
    }
    
    selected_mode = st.radio(
        "Yanıt modu:",
        options=list(mode_options.keys()),
        index=0,
        horizontal=True
    )
    st.session_state.force_mode = mode_options[selected_mode]
    
    if st.session_state.force_mode:
        st.info(f"📌 Override aktif: **{selected_mode}** modu zorlanıyor")

st.divider()

# Önceki mesajları göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı mesajı
user_input = st.chat_input("Sorunuzu yazınız...")

if user_input:
    # Kullanıcı mesajını ekle
    st.session_state.messages.append(
        {
            "role": "user", 
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Smart Chat API çağrısı
    payload = {
        "session_id": st.session_state.session_id,
        "message": user_input,
        "force_mode": st.session_state.force_mode
    }

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum..."):
            try:
                response = requests.post(SMART_API_URL, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result["answer"]
                    mode_used = result["mode_used"]
                    mode_explanation = result["mode_explanation"]
                    
                    # Mod göstergesi
                    st.caption(mode_explanation)
                    
                    # Yanıt
                    st.markdown(answer)
                    
                    # Mesajı kaydet (mod bilgisiyle)
                    st.session_state.messages.append(
                        {
                            "role": "assistant", 
                            "content": f"*{mode_explanation}*\n\n{answer}"
                        }
                    )
                else:
                    st.error(f"API hatası: {response.status_code}")
            except requests.exceptions.Timeout:
                st.error("⏱️ İstek zaman aşımına uğradı. Lütfen tekrar deneyin.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 API'ye bağlanılamadı. Backend çalışıyor mu?")
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")