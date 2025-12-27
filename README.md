# 🤖 Smart LLM Assistant

LLM tabanlı akıllı yazılım mimari asistanı. Semantic Router ile otomatik mod seçimi, web arama ve RAG (Retrieval-Augmented Generation) özellikleri.

## ✨ Özellikler

- **🧠 Akıllı Yönlendirme**: LLM mesajınızı analiz edip en uygun kaynağı otomatik seçer
- **💬 Chat**: Yazılım mimarisi, tasarım desenleri, SOLID prensipleri hakkında sohbet
- **🌐 Web Search**: Güncel bilgiler için web'de arama (SerpAPI)
- **📄 RAG**: Yüklediğiniz dokümanlarda arama (PDF, DOCX, TXT)

## 🎓 Öğrenim Hedefleri ve Kazanımlar

Bu uygulamayı kullanan ve inceleyen geliştiriciler aşağıdaki yetkinlikleri elde edecektir:

1.  **Modern AI Mimarilerini Kavrama**: LLM uygulamalarında RAG (Retrieval-Augmented Generation) ve Semantic Routing gibi ileri seviye tekniklerin nasıl bir araya getirildiğini ve gerçek senaryolarda nasıl çalıştığını deneyimleyeceksiniz.
2.  **Hızlı ve Akıllı Doküman Analizi**: Kapsamlı teknik dokümanlar (PDF, DOCX, TXT) içerisinden manuel arama yapmaya gerek kalmadan saniyeler içinde spesifik bilgileri çekebilir ve kompleks yapıları özetleyebilirsiniz.
3.  **Mimari Karar Verme Yetkinliği**: Asistanın sunduğu trade-off (ödünleşim) analizleri ve tasarım desenleri önerileri sayesinde, yazılım süreçlerinde daha sağlam ve gerekçeli mimari kararlar alma becerisi kazanacaksınız.
4.  **Gerçek Zamanlı Veri Entegrasyonu**: Statik model bilgilerini canlı web verileriyle (SerpAPI) harmanlayarak, en güncel teknolojik trendler ve kütüphane sürümleri hakkında doğru ve doğrulanabilir bilgiye ulaşma yetisi edineceksiniz.

## 🛠️ Teknolojiler

- **Backend**: FastAPI + LangChain
- **LLM**: Google Gemini API (gemini-flash-lite-latest)
- **Embeddings**: Google Generative AI Embeddings
- **Vector Store**: FAISS
- **Frontend**: Streamlit
- **Web Search**: SerpAPI

## 📦 Kurulum

### 1. Gemini API Key

[Google AI Studio](https://aistudio.google.com/apikey) adresinden ücretsiz API key alın.

### 2. Proje Kurulumu

```bash
# Repo'yu klonla
git clone https://github.com/durmazsena/smart-llm-assistant.git
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
# GOOGLE_API_KEY=your_key_here
# SERPAPI_KEY=your_key_here
```

## 🚀 Çalıştırma

### Backend (FastAPI)

```bash
# Proje kök dizinindeyken:
uvicorn backend.main:app --reload
```

### Frontend (Streamlit)

```bash
cd frontend
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
smart-llm-assistant/
├── backend/
│   ├── main.py              # FastAPI backend + Gemini API
│   ├── semantic_router.py   # LLM-based intent detection
│   └── __init__.py
├── frontend/
│   ├── app_streamlit.py     # Streamlit frontend
│   └── .streamlit/          # Streamlit tema ayarları
├── requirements.txt         # Python bağımlılıkları
├── .env                     # Ortam değişkenleri (gitignore'da)
└── .env.example             # Örnek ortam değişkenleri
```

## 📝 Lisans

MIT
