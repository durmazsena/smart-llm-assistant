"""
Semantic Router - Dinamik LLM-based Intent Detection

Kullanıcı mesajlarını analiz ederek doğru endpoint'e yönlendirir:
- chat: Genel yazılım/mimari soruları
- web_search: Güncel bilgi gerektiren sorular
- rag: Yüklü dokümana referans içeren sorular
"""

from langchain_community.chat_models import ChatOllama


class SemanticRouter:
    """LLM tabanlı akıllı yönlendirici"""
    
    def __init__(self, llm: ChatOllama):
        self.llm = llm
    
    def route(self, message: str, has_document: bool = False) -> str:
        """
        Kullanıcı mesajını analiz ederek uygun modu belirler.
        
        Args:
            message: Kullanıcı mesajı
            has_document: Session'da yüklü doküman var mı
            
        Returns:
            "chat", "web_search" veya "rag"
        """
        
        # RAG context bilgisi
        rag_context = "Kullanıcının yüklediği bir doküman VAR. " if has_document else ""
        
        prompt = f"""Kullanıcının mesajını analiz et ve hangi moda yönlendirileceğini belirle.

MODLAR:
- chat: Genel yazılım/mimari soruları, kavram açıklamaları, kod örnekleri, teorik bilgiler
- web_search: Güncel bilgi gerektiren sorular (2024, son, güncel, yeni, trend, haberler, karşılaştırma)
- rag: {rag_context}Dokümana/dosyaya referans içeren sorular (dosyada, belgede, yüklediğim, dokümanda)

KURALLAR:
1. Güncel tarih/yıl içeren sorular, bugünün tarihi, etkinlik arama → web_search
2. "En iyi", "karşılaştır", "önerir misin" gibi sorular → web_search
3. Dosya/doküman referansı varsa VE doküman yüklüyse → rag
4. Genel kavram açıklaması, kod örneği → chat

MESAJ: {message}

SADECE şu kelimelerden BİRİNİ yaz (başka hiçbir şey yazma): chat, web_search, rag"""

        try:
            result = self.llm.invoke(prompt)
            route = result.content.strip().lower()
            
            # İlk kelimeyi al (bazen LLM fazladan açıklama ekleyebilir)
            route = route.split()[0] if route else "chat"
            
            # Noktalama işaretlerini temizle
            route = route.strip(".,!?")
            
            # Geçerli route kontrolü
            if route not in ["chat", "web_search", "rag"]:
                return "chat"
            
            # RAG sadece doküman varsa kullanılabilir
            if route == "rag" and not has_document:
                return "chat"
            
            return route
            
        except Exception as e:
            print(f"SemanticRouter error: {e}")
            return "chat"
    
    def get_route_explanation(self, route: str) -> str:
        """Route için kullanıcıya gösterilecek açıklama"""
        explanations = {
            "chat": "💬 Asistan bilgisiyle yanıtlanıyor",
            "web_search": "🌐 Web'de aranıyor",
            "rag": "📄 Dokümanda aranıyor"
        }
        return explanations.get(route, "💬 Yanıtlanıyor")
