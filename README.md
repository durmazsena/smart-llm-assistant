# 🤖 Yazılım Mimarı Asistanı

LLM tabanlı akıllı yazılım mimari asistanı. Semantic Router ile otomatik mod seçimi, web arama ve RAG (Retrieval-Augmented Generation) özellikleri.

## ✨ Özellikler

- **🧠 Akıllı Yönlendirme**: LLM mesajınızı analiz edip en uygun kaynağı otomatik seçer
- **💬 Chat**: Yazılım mimarisi, tasarım desenleri, SOLID prensipleri hakkında sohbet
- **🌐 Web Search**: Güncel bilgiler için web'de arama (SerpAPI)
- **📄 RAG**: Yüklediğiniz dokümanlarda arama (PDF, DOCX, TXT)

## 🛠️ Teknolojiler

- **Backend**: FastAPI + LangChain
- **LLM**: Ollama (gemma3:4b)
- **Vector Store**: FAISS
- **Frontend**: Streamlit
- **Web Search**: SerpAPI

## 📦 Kurulum

### 1. Ollama Kurulumu

```bash
# macOS
brew install ollama

# Model indir
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

### 2. Proje Kurulumu

```bash
# Repo'yu klonla
git clone https://github.com/YOUR_USERNAME/smart-llm-assistant.git
cd smart-llm-assistant

# Sanal ortam oluştur
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 3. Ortam Değişkenleri

```bash
# .env.example'ı kopyala
cp .env.example .env

# .env dosyasını düzenle ve API key'leri ekle
```

## 🚀 Çalıştırma

### Backend (FastAPI)

```bash
uvicorn main:app --reload
```

### Frontend (Streamlit)

```bash
streamlit run app_streamlit.py
```

Tarayıcıda `http://localhost:8501` adresine gidin.

## 📡 API Endpoints

| Endpoint | Açıklama |
|----------|----------|
| `POST /smart_chat` | Akıllı yönlendirmeli chat (önerilen) |
| `POST /chat` | Direkt LLM chat |
| `POST /web_search` | Web araması |
| `POST /rag/upload` | Doküman yükleme |
| `POST /rag/query` | Dokümanda arama |

## 🏗️ Proje Yapısı

```
btk_asistan/
├── main.py              # FastAPI backend
├── semantic_router.py   # LLM-based intent detection
├── app_streamlit.py     # Streamlit frontend
├── requirements.txt     # Python bağımlılıkları
├── .env                 # Ortam değişkenleri (gitignore'da)
└── .env.example         # Örnek ortam değişkenleri
```

## 📝 Lisans

MIT
