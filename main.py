import os
import requests
import tempfile
import shutil
from typing import Dict, List, Optional
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# LangChain imports
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings

# FastAPI imports
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

# Document processing
from docx import Document as DocxDocument

# Semantic Router
from semantic_router import SemanticRouter

# .env dosyasını yükle
load_dotenv()

app = FastAPI(title="Yazılım Mimarı Asistanı")

# ---------------------------
# 1) LLM (Ollama + Gemma3)
# ---------------------------
llm = ChatOllama(
    model="gemma3:4b",
    temperature=0.3,
)

# ---------------------------
# 2) System prompt (senin promptun)
# ---------------------------
system_prompt =  """
Sen deneyimli bir Yazılım Mimarı Asistanısın. Görevin, kullanıcıya yazılım tasarımı, mimari desenler, teknoloji seçimi ve en iyi uygulamalar konusunda rehberlik etmektir.
Kullanıcı sohbet etmek istediğinde sohbetine eşlik et ve mevcut görevine yönlendirici şekilde yanıt ver.

Aşağıdaki ilkeleri benimse:
1. **Analitik Yaklaşım**: Sorunları parçalara ayır, trade-off (ödünleşim) analizleri yap (örn. Performans vs Maliyet).
2. **Desen Odaklılık**: Uygun olduğunda Gang of Four (GoF), SOLID prensipleri, Clean Architecture gibi kavramlara atıfta bulun.
3. **Teknoloji Agnostik**: Belirli bir dile veya framework'e takılı kalmadan, genel geçer mimari doğruları savun, ancak istendiğinde spesifik öneriler sun.
4. **Güvenlik ve Ölçeklenebilirlik**: Her tasarım önerisinde güvenlik ve ölçeklenebilirliği varsayılan olarak göz önünde bulundur.
5. **Net ve Gerekçeli**: Bir çözüm önerirken "neden" o çözümü seçtiğini açıkla. Alternatifleri de kısaca belirt.

Kullanıcı sana bir sistem gereksinimi veya sorunu sunduğunda, profesyonel, eğitici ve çözüm odaklı bir dille yanıt ver.

"""

# ---------------------------
# 3) Prompt şablonu (history + user input)
# ---------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# LCEL chain
chain = prompt | llm

# ---------------------------
# 4) Memory store (session bazlı)
# ---------------------------
_store: Dict[str, InMemoryChatMessageHistory] = {}

def get_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _store:
        _store[session_id] = InMemoryChatMessageHistory()
    return _store[session_id]

# RunnableWithMessageHistory -> otomatik history ekler/tutar
chatbot = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="input",      # kullanıcı girişi hangi key'de
    history_messages_key="history",  # geçmiş promptta hangi isimle geçiyor
)

# ---------------------------
# 5) Request/Response model
# ---------------------------
class ChatRequest(BaseModel): #llm input
    session_id: str
    message: str

class ChatResponse(BaseModel): #llm output
    answer: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = chatbot.invoke(
        {"input": request.message},
        config={"configurable": {"session_id": request.session_id}}
    )
    return ChatResponse(answer=result.content)


# ---------------------------
# 6) Web search (SerpAPI)
# ---------------------------
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def serpapi_search(query: str) -> dict:
    """SerpAPI ile Google araması yap ve ilk sonucun URL'sini döndür"""
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "hl": "tr",
        "gl": "tr",
        "num": 5
    }
    
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        data = response.json()
        
        if "organic_results" in data and len(data["organic_results"]) > 0:
            first_result = data["organic_results"][0]
            return {
                "url": first_result.get("link", ""),
                "title": first_result.get("title", ""),
                "snippet": first_result.get("snippet", "")
            }
        return None
            
    except Exception as e:
        return None


def fetch_url_content(url: str, max_chars: int = 3000) -> str:
    """URL'den içerik çek ve temizle"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Script ve style taglerini kaldır
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        # Metni al
        text = soup.get_text(separator=" ", strip=True)
        
        # Fazla boşlukları temizle
        text = " ".join(text.split())
        
        return text[:max_chars]
        
    except Exception as e:
        return ""


class WebSearchRequest(BaseModel):
    session_id: str
    message: str


class WebSearchResponse(BaseModel):
    answer: str


@app.post("/web_search", response_model=WebSearchResponse)
async def web_search(request: WebSearchRequest):
    """Web'de ara, ilk sonucu çek ve LLM ile özetle"""
    
    # 1. SerpAPI ile arama yap
    search_result = serpapi_search(request.message)
    
    if not search_result:
        return WebSearchResponse(answer="❌ Arama sonucu bulunamadı.")
    
    # 2. URL'den içerik çek
    content = fetch_url_content(search_result["url"])
    
    if not content:
        # İçerik çekilemezse sadece snippet döndür
        return WebSearchResponse(
            answer=f"🌐 **{search_result['title']}**\n\n{search_result['snippet']}\n\n🔗 {search_result['url']}"
        )
    
    # 3. LLM ile cevap oluştur
    web_prompt = f"""Aşağıdaki web sayfası içeriğine dayanarak kullanıcının sorusunu yanıtla.
Yanıtı Türkçe ve akıcı bir dille oluştur. Kaynak bilgisini de belirt.

WEB SAYFASI İÇERİĞİ:
{content}

KULLANICI SORUSU: {request.message}

KAYNAK: {search_result['url']}

YANIT:"""
    
    result = llm.invoke(web_prompt)
    answer = f"{result.content}\n\n📚 **Kaynak:** [{search_result['title']}]({search_result['url']})"
    
    return WebSearchResponse(answer=answer)


# ---------------------------
# 7) RAG (FAISS + Ollama Embeddings)
# ---------------------------

# Embedding modeli (Ollama ile)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Global FAISS index (session bazlı tutulabilir)
_faiss_stores: Dict[str, FAISS] = {}

def load_document(file_path: str, file_type: str) -> List[str]:
    """Dosyayı yükle ve metin listesi döndür"""
    texts = []
    
    if file_type == "pdf":
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        texts = [page.page_content for page in pages]
    
    elif file_type == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            texts = [f.read()]
    
    elif file_type == "docx":
        doc = DocxDocument(file_path)
        texts = [para.text for para in doc.paragraphs if para.text.strip()]
    
    return texts

def chunk_texts(texts: List[str], chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """Metinleri chunk'lara böl"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = []
    for text in texts:
        chunks.extend(splitter.split_text(text))
    return chunks


class RAGUploadResponse(BaseModel):
    status: str
    chunks: int
    message: str


@app.post("/rag/upload", response_model=RAGUploadResponse)
async def rag_upload(session_id: str, file: UploadFile = File(...)):
    """Dosya yükle, chunk'la ve FAISS index'e ekle"""
    try:
        # Dosya uzantısını al
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ["pdf", "txt", "docx"]:
            return RAGUploadResponse(status="error", chunks=0, message="Desteklenmeyen dosya formatı!")
        
        # Geçici dosyaya kaydet
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Dosyayı yükle ve chunk'la
        texts = load_document(tmp_path, file_ext)
        chunks = chunk_texts(texts)
        
        # Geçici dosyayı sil
        os.unlink(tmp_path)
        
        if not chunks:
            return RAGUploadResponse(status="error", chunks=0, message="Dosyadan metin çıkarılamadı!")
        
        # FAISS index oluştur
        faiss_store = FAISS.from_texts(chunks, embeddings)
        _faiss_stores[session_id] = faiss_store
        
        return RAGUploadResponse(
            status="success",
            chunks=len(chunks),
            message=f"✅ {file.filename} başarıyla yüklendi! {len(chunks)} chunk oluşturuldu."
        )
        
    except Exception as e:
        return RAGUploadResponse(status="error", chunks=0, message=f"Hata: {str(e)}")


class RAGQueryRequest(BaseModel):
    session_id: str
    message: str


class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[str]


@app.post("/rag/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    """Soru sor, ilgili chunk'ları bul ve LLM ile cevapla"""
    session_id = request.session_id
    
    # FAISS index var mı kontrol et
    if session_id not in _faiss_stores:
        return RAGQueryResponse(
            answer="⚠️ Önce bir dosya yüklemeniz gerekiyor!",
            sources=[]
        )
    
    faiss_store = _faiss_stores[session_id]
    
    # Benzer chunk'ları bul (top 3)
    docs = faiss_store.similarity_search(request.message, k=3)
    
    if not docs:
        return RAGQueryResponse(
            answer="❌ İlgili bilgi bulunamadı.",
            sources=[]
        )
    
    # Context oluştur
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # RAG prompt
    rag_prompt = f"""Aşağıdaki bağlam bilgisini kullanarak kullanıcının sorusunu yanıtla.
Yanıtı sadece verilen bağlama dayandır. Bağlamda bilgi yoksa "Bu bilgi dokümanda bulunamadı" de.

BAĞLAM:
{context}

SORU: {request.message}

CEVAP:"""
    
    # LLM ile cevapla
    result = llm.invoke(rag_prompt)
    
    return RAGQueryResponse(
        answer=result.content,
        sources=[doc.page_content[:100] + "..." for doc in docs]
    )


# ---------------------------
# 8) Smart Chat (Semantic Router)
# ---------------------------

# Router instance
semantic_router = SemanticRouter(llm)


class SmartChatRequest(BaseModel):
    session_id: str
    message: str
    force_mode: Optional[str] = None  # "chat", "web_search", "rag" veya None (otomatik)


class SmartChatResponse(BaseModel):
    answer: str
    mode_used: str
    mode_explanation: str
    sources: List[str] = []


@app.post("/smart_chat", response_model=SmartChatResponse)
async def smart_chat(request: SmartChatRequest):
    """
    Akıllı chat endpoint - mesajı analiz edip doğru moda yönlendirir.
    
    - force_mode belirtilmişse o mod kullanılır (override)
    - force_mode None ise LLM otomatik karar verir
    """
    session_id = request.session_id
    message = request.message
    
    # Doküman yüklü mü kontrol et
    has_document = session_id in _faiss_stores
    
    # Mod belirleme
    if request.force_mode and request.force_mode in ["chat", "web_search", "rag"]:
        mode = request.force_mode
    else:
        mode = semantic_router.route(message, has_document=has_document)
    
    mode_explanation = semantic_router.get_route_explanation(mode)
    
    # Moda göre yönlendir
    if mode == "chat":
        result = chatbot.invoke(
            {"input": message},
            config={"configurable": {"session_id": session_id}}
        )
        return SmartChatResponse(
            answer=result.content,
            mode_used=mode,
            mode_explanation=mode_explanation
        )
    
    elif mode == "web_search":
        # Web search logic
        search_result = serpapi_search(message)
        
        if not search_result:
            return SmartChatResponse(
                answer="❌ Web araması sonuç bulunamadı. Normal yanıt veriyorum.",
                mode_used="chat",
                mode_explanation="💬 Web araması başarısız, asistan yanıtlıyor"
            )
        
        content = fetch_url_content(search_result["url"])
        
        if not content:
            answer = f"🌐 **{search_result['title']}**\n\n{search_result['snippet']}\n\n🔗 {search_result['url']}"
        else:
            web_prompt = f"""Aşağıdaki web sayfası içeriğine dayanarak kullanıcının sorusunu yanıtla.
Yanıtı Türkçe ve akıcı bir dille oluştur. Kaynak bilgisini de belirt.

WEB SAYFASI İÇERİĞİ:
{content}

KULLANICI SORUSU: {message}

KAYNAK: {search_result['url']}

YANIT:"""
            result = llm.invoke(web_prompt)
            answer = f"{result.content}\n\n📚 **Kaynak:** [{search_result['title']}]({search_result['url']})"
        
        return SmartChatResponse(
            answer=answer,
            mode_used=mode,
            mode_explanation=mode_explanation,
            sources=[search_result["url"]]
        )
    
    elif mode == "rag":
        # RAG sadece doküman varsa
        if not has_document:
            return SmartChatResponse(
                answer="⚠️ Henüz bir doküman yüklenmemiş. Lütfen önce bir dosya yükleyin.",
                mode_used="chat",
                mode_explanation="📄 Doküman bulunamadı"
            )
        
        faiss_store = _faiss_stores[session_id]
        docs = faiss_store.similarity_search(message, k=3)
        
        if not docs:
            return SmartChatResponse(
                answer="❌ Dokümanda ilgili bilgi bulunamadı.",
                mode_used=mode,
                mode_explanation=mode_explanation
            )
        
        context = "\n\n".join([doc.page_content for doc in docs])
        
        rag_prompt = f"""Aşağıdaki bağlam bilgisini kullanarak kullanıcının sorusunu yanıtla.
Yanıtı sadece verilen bağlama dayandır. Bağlamda bilgi yoksa "Bu bilgi dokümanda bulunamadı" de.

BAĞLAM:
{context}

SORU: {message}

CEVAP:"""
        
        result = llm.invoke(rag_prompt)
        
        return SmartChatResponse(
            answer=result.content,
            mode_used=mode,
            mode_explanation=mode_explanation,
            sources=[doc.page_content[:100] + "..." for doc in docs]
        )
    
    # Fallback
    return SmartChatResponse(
        answer="Bir hata oluştu, lütfen tekrar deneyin.",
        mode_used="chat",
        mode_explanation="⚠️ Hata"
    )


"""
# ---------------------------
# 6) While döngüsü ile chat
# ---------------------------
print("Yazılım Mimarı Asistanı (çıkmak için 'exit')\n")

session_id = "yazılım_session_1"  # istersen kullanıcıya göre dinamik yaparsın

while True:
    user_input = input("Sen: ").strip()
    if user_input.lower() in ["exit", "quit", "q"]:
        print("Asistan: Görüşürüz!")
        break

    # invoke sırasında config ile session_id veriyoruz
    result = chatbot.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )

    # ChatOllama sonucu genelde AIMessage döner, .content ile yazdır
    print(f"Asistan: {result.content}\n")
"""