# ============================================
# 🚀 IntelliDoc RAG - النسخة المستقرة
# ============================================

import streamlit as st
import os
import sys
import json
import hashlib
import pickle
import re
import io
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# استيراد المكتبات
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


# ═══════════════════════════════════════════════════════════
# إعداد الصفحة
# ═══════════════════════════════════════════════════════════

st.set_page_config(
    page_title="🧠 IntelliDoc RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ═══════════════════════════════════════════════════════════
# CSS المخصص
# ═══════════════════════════════════════════════════════════

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* الأساسي */
* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0a0c10;
    color: #e2e8f0;
    -webkit-font-smoothing: antialiased;
}

/* تأثيرات الزجاج */
.glass-panel {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.glass-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    border-color: rgba(255, 255, 255, 0.15);
    background: rgba(255, 255, 255, 0.04);
    transform: translateY(-2px);
}

/* الهيدر */
.main-header {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.main-header h1 {
    font-size: 2.5rem;
    font-weight: 600;
    margin: 0;
    color: #f1f5f9;
    letter-spacing: -0.02em;
}

.main-header p {
    color: #94a3b8;
    margin-top: 0.75rem;
    font-weight: 300;
}

/* بطاقة الميزات */
.feature-box {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 1.75rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.feature-box:hover {
    transform: translateY(-4px);
    border-color: rgba(56, 189, 248, 0.3);
    box-shadow: 0 20px 40px rgba(56, 189, 248, 0.1);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
}

.feature-title {
    font-weight: 500;
    color: #f1f5f9;
    margin-bottom: 0.5rem;
    font-size: 1rem;
}

.feature-desc {
    font-size: 0.85rem;
    color: #64748b;
    font-weight: 300;
}

/* المحادثة */
.chat-container {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 24px;
    padding: 1.5rem;
    min-height: 50vh;
    max-height: 60vh;
    overflow-y: auto;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

/* الرسائل */
.message {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.message-avatar {
    width: 45px;
    height: 45px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.avatar-user {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.avatar-ai {
    background: linear-gradient(135deg, #10b981, #059669);
}

.message-bubble {
    background: rgba(30, 41, 59, 0.6);
    border-radius: 20px;
    border-top-left-radius: 6px;
    padding: 1rem 1.25rem;
    max-width: 80%;
    line-height: 1.7;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.message.user .message-bubble {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    border-radius: 20px;
    border-top-right-radius: 6px;
    border-top-left-radius: 20px;
    margin-left: auto;
    border: none;
}

.message-sources {
    background: rgba(56, 189, 248, 0.08);
    border-left: 3px solid #38bdf8;
    border-radius: 0 16px 16px 0;
    padding: 0.75rem 1rem;
    margin-top: 0.75rem;
    font-size: 0.85rem;
}

.sources-title {
    color: #38bdf8;
    font-weight: 500;
    margin-bottom: 0.5rem;
}

/* مؤشر الكتابة */
.typing-indicator {
    display: flex;
    gap: 5px;
    padding: 0.5rem;
}

.typing-dot {
    width: 8px;
    height: 8px;
    background: #38bdf8;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) { animation-delay: 0s; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

/* المقاييس */
.metric-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 1.75rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.metric-card:hover {
    border-color: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
}

.metric-value {
    font-size: 2.25rem;
    font-weight: 600;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
}

.metric-label {
    color: #64748b;
    font-size: 0.85rem;
    margin-top: 0.5rem;
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* المستندات */
.doc-item {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.doc-item:hover {
    border-color: rgba(56, 189, 248, 0.3);
    transform: translateX(4px);
    background: rgba(255, 255, 255, 0.04);
}

.doc-info {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.doc-icon {
    width: 45px;
    height: 45px;
    background: rgba(56, 189, 248, 0.1);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    border: 1px solid rgba(56, 189, 248, 0.2);
}

/* الشريط الجانبي */
.css-1d391kg {
    background: #0d1117 !important;
}

section[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* الأزرار */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 500 !important;
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.25) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    letter-spacing: 0.01em;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(59, 130, 246, 0.35) !important;
}

/* حقول الإدخال */
.stTextInput > div > div > input {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15) !important;
}

.stTextInput > div > div > input::placeholder {
    color: #475569 !important;
}

/* شريط التقدم */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #38bdf8, #818cf8) !important;
    border-radius: 10px !important;
}

/* علامات التبويب */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: rgba(15, 23, 42, 0.4);
    padding: 0.5rem;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.25rem !important;
    color: #64748b !important;
    font-weight: 400 !important;
    transition: all 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #94a3b8 !important;
    background: rgba(255, 255, 255, 0.03) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    color: white !important;
    font-weight: 500 !important;
}

/* شريط التمرير */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: #0a0c10;
}

::-webkit-scrollbar-thumb {
    background: #1e293b;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #334155;
}

/* تخصيصات إضافية */
div[data-testid="stFileUploader"] {
    background: rgba(15, 23, 42, 0.4);
    border: 2px dashed rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2rem;
    transition: all 0.3s ease;
}

div[data-testid="stFileUploader"]:hover {
    border-color: rgba(56, 189, 248, 0.3);
    background: rgba(15, 23, 42, 0.6);
}

div[data-testid="stFileUploader"] label {
    color: #94a3b8 !important;
}

/* Expander في الشريط الجانبي */
.streamlit-expanderHeader {
    background: rgba(30, 41, 59, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-weight: 500 !important;
}

.streamlit-expanderContent {
    background: rgba(15, 23, 42, 0.3) !important;
    border: 1px solid rgba(255, 255, 255, 0.04) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
}

/* Slider في الشريط الجانبي */
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #38bdf8, #818cf8) !important;
}

.stSlider > div > div > div {
    background: rgba(255, 255, 255, 0.1) !important;
}

/* Metric في الشريط الجانبي */
div[data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 1rem;
}

div[data-testid="stMetric"] label {
    color: #64748b !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
}
</style>
"""


# ═══════════════════════════════════════════════════════════
# فئة معالج المستندات
# ═══════════════════════════════════════════════════════════

class DocumentProcessor:
    """معالج المستندات"""
    
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def get_file_icon(self, filename):
        """الحصول على أيقونة الملف"""
        ext = filename.lower().split('.')[-1]
        icons = {
            'pdf': '📕',
            'docx': '📘',
            'doc': '📘',
            'txt': '📄',
            'csv': '📊',
            'md': '📝',
            'xlsx': '📗',
            'xls': '📗'
        }
        return icons.get(ext, '📎')
    
    def extract_text(self, file):
        """استخراج النص من الملف"""
        filename = file.name.lower()
        
        if filename.endswith('.pdf') and HAS_PDF:
            return self._extract_pdf(file)
        elif filename.endswith('.docx') and HAS_DOCX:
            return self._extract_docx(file)
        elif filename.endswith('.txt'):
            return self._extract_txt(file)
        elif filename.endswith('.csv'):
            return self._extract_txt(file)
        elif filename.endswith('.md'):
            return self._extract_txt(file)
        else:
            # محاولة قراءة كنص
            return self._extract_txt(file)
    
    def _extract_pdf(self, file):
        """استخراج نص PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            st.error(f"خطأ في قراءة PDF: {e}")
            return ""
    
    def _extract_docx(self, file):
        """استخراج نص DOCX"""
        try:
            doc = Document(io.BytesIO(file.read()))
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            st.error(f"خطأ في قراءة DOCX: {e}")
            return ""
    
    def _extract_txt(self, file):
        """استخراج نص عادي"""
        try:
            return file.read().decode("utf-8")
        except:
            try:
                return file.read().decode("latin-1")
            except:
                return ""
    
    def split_text(self, text, source=""):
        """تقسيم النص إلى أجزاء"""
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        
        if not text:
            return []
        
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = ""
        index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(para) > self.chunk_size:
                if current_chunk:
                    chunks.append({
                        'index': index,
                        'text': current_chunk,
                        'source': source,
                        'words': len(current_chunk.split())
                    })
                    index += 1
                    current_chunk = ""
                
                # تقسيم الفقرة الطويلة
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sent in sentences:
                    if len(current_chunk) + len(sent) > self.chunk_size:
                        if current_chunk:
                            chunks.append({
                                'index': index,
                                'text': current_chunk,
                                'source': source,
                                'words': len(current_chunk.split())
                            })
                            index += 1
                        current_chunk = sent
                    else:
                        current_chunk = current_chunk + " " + sent if current_chunk else sent
            else:
                if len(current_chunk) + len(para) > self.chunk_size:
                    if current_chunk:
                        chunks.append({
                            'index': index,
                            'text': current_chunk,
                            'source': source,
                            'words': len(current_chunk.split())
                        })
                        index += 1
                    current_chunk = para
                else:
                    current_chunk = current_chunk + "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append({
                'index': index,
                'text': current_chunk,
                'source': source,
                'words': len(current_chunk.split())
            })
        
        return chunks


# ═══════════════════════════════════════════════════════════
# فئة قاعدة البيانات المتجهات
# ═══════════════════════════════════════════════════════════

class VectorStore:
    """قاعدة بيانات متجهات بسيطة ومستقرة"""
    
    def __init__(self, persist_dir="./vector_db"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)
        
        self.documents = []
        self.embeddings = []
        self.embedder = None
        
        if HAS_EMBEDDINGS:
            try:
                with st.spinner("جاري تحميل نموذج البحث..."):
                    self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                st.success("✅ تم تحميل نموذج البحث")
            except Exception as e:
                st.warning(f"⚠️ لم يتم تحميل النموذج: {e}")
                self.embedder = None
    
    def _get_embedding(self, text):
        """الحصول على ترميز للنص"""
        if self.embedder:
            return self.embedder.encode(text).tolist()
        
        # ترميز بديل بسيط
        if HAS_NUMPY:
            hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
            np.random.seed(hash_val % (2**32))
            return np.random.randn(384).tolist()
        
        return [0] * 384
    
    def add_documents(self, documents):
        """إضافة مستندات"""
        for doc in documents:
            embedding = self._get_embedding(doc['text'])
            self.documents.append(doc)
            self.embeddings.append(embedding)
    
    def search(self, query, top_k=5):
        """البحث في المستندات"""
        if not self.documents:
            return []
        
        query_emb = self._get_embedding(query)
        
        # حساب التشابه
        scores = []
        for i, doc_emb in enumerate(self.embeddings):
            score = self._cosine_similarity(query_emb, doc_emb)
            scores.append((i, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in scores[:top_k]:
            doc = self.documents[idx].copy()
            doc['score'] = round(float(score) * 100, 1)
            results.append(doc)
        
        return results
    
    def _cosine_similarity(self, a, b):
        """حساب التشابه الزاوي"""
        if HAS_NUMPY:
            a, b = np.array(a), np.array(b)
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)
        
        # حساب يدوي
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot_product / (norm_a * norm_b + 1e-8)
    
    def clear(self):
        """مسح كل البيانات"""
        self.documents = []
        self.embeddings = []
    
    def get_stats(self):
        """إحصائيات المخزن"""
        sources = {}
        for doc in self.documents:
            src = doc.get('source', 'غير معروف')
            sources[src] = sources.get(src, 0) + 1
        
        return {
            'total_chunks': len(self.documents),
            'total_sources': len(sources)
        }


# ═══════════════════════════════════════════════════════════
# فئة محرك المحادثة
# ═══════════════════════════════════════════════════════════

class ChatEngine:
    """محرك المحادثة"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.openrouter_key = "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"
    
    def generate_response(self, query, context_docs):
        """توليد الرد"""
        # بناء السياق
        context = "\n\n".join([
            f"[المصدر {i+1}: {doc.get('source', 'غير معروف')}]\n{doc['text']}"
            for i, doc in enumerate(context_docs)
        ])
        
        sources = list(set([doc.get('source', 'غير معروف') for doc in context_docs]))
        
        # محاولة استخدام OpenAI
        if self.api_key:
            answer = self._generate_with_openai(query, context)
        else:
            answer = self._generate_fallback(query, context)
        
        # حساب الثقة
        confidence = 0
        if context_docs:
            confidence = sum(doc.get('score', 0) for doc in context_docs) / len(context_docs)
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': round(confidence, 1)
        }
    
    def _generate_with_openai(self, query, context):
        """توليد باستخدام OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_key
            )
            
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "أنت مساعد ذكي. أجب بناءً على المستندات فقط بالعربية."},
                    {"role": "user", "content": f"المستندات:\n{context[:3000]}\n\nالسؤال: {query}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except:
            return self._generate_fallback(query, context)
    
    def _generate_fallback(self, query, context):
        """رد بديل"""
        if not context.strip():
            return "📭 لا توجد مستندات للبحث فيها. يرجى رفع ملفات أولاً."
        
        # عرض السياق المُ找回
        preview = context[:600] + "..." if len(context) > 600 else context
        
        return f"""📋 **نتائج البحث:**

{preview}

---
💡 **نصيحة:** أضف مفتاح OpenAI API للحصول على إجابات ذكية migliore."""


# ═══════════════════════════════════════════════════════════
# تهيئة الجلسة
# ═══════════════════════════════════════════════════════════

def init_session():
    """تهيئة متغيرات الجلسة"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    
    if 'processor' not in st.session_state:
        st.session_state.processor = DocumentProcessor()
    
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'chunk_size': 500,
            'chunk_overlap': 50,
            'top_k': 5
        }
    
    if 'stats' not in st.session_state:
        st.session_state.stats = {
            'queries': 0,
            'response_time': []
        }


# ═══════════════════════════════════════════════════════════
# مكونات الواجهة
# ═══════════════════════════════════════════════════════════

def render_header():
    """عرض الهيدر"""
    st.markdown("""
    <div class="main-header">
        <h1>🧠 IntelliDoc RAG</h1>
        <p>نظام ذكي للاستعلام عن المستندات باستخدام الذكاء الاصطناعي</p>
    </div>
    """, unsafe_allow_html=True)


def render_features():
    """عرض المميزات"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📄</div>
            <div class="feature-title">متعدد الأنواع</div>
            <div class="feature-desc">PDF, Word, TXT, CSV</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">بحث ذكي</div>
            <div class="feature-desc">بحث دلالي متقدم</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">💬</div>
            <div class="feature-title">محادثة طبيعية</div>
            <div class="feature-desc">إجابات فورية</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📊</div>
            <div class="feature-title">تحليلات</div>
            <div class="feature-desc">إحصائيات مفصلة</div>
        </div>
        """, unsafe_allow_html=True)


def render_sidebar():
    """عرض الشريط الجانبي"""
    with st.sidebar:
        st.markdown("## ⚙️ الإعدادات")
        
        # إعدادات المعالجة
        with st.expander("📄 معالجة المستندات", expanded=True):
            st.session_state.settings['chunk_size'] = st.slider(
                "حجم الجزء", 100, 1000, 
                st.session_state.settings['chunk_size']
            )
            st.session_state.settings['chunk_overlap'] = st.slider(
                "التداخل", 0, 200, 
                st.session_state.settings['chunk_overlap']
            )
        
        # إعدادات البحث
        with st.expander("🔍 البحث", expanded=True):
            st.session_state.settings['top_k'] = st.slider(
                "عدد النتائج", 1, 10, 
                st.session_state.settings['top_k']
            )
        
        # OpenAI API
        with st.expander("🔑 OpenAI (اختياري)", expanded=False):
            api_key = st.text_input("مفتاح API", type="password")
            if api_key:
                os.environ['OPENAI_API_KEY'] = api_key
        
        st.markdown("---")
        
        # الإحصائيات
        st.markdown("### 📈 إحصائيات")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 المستندات", len(st.session_state.documents))
        with col2:
            st.metric("❓ الاستعلامات", st.session_state.stats['queries'])
        
        if st.session_state.vector_store:
            stats = st.session_state.vector_store.get_stats()
            st.metric("📝 الأجزاء", stats['total_chunks'])
        
        st.markdown("---")
        
        # المستندات المحملة
        st.markdown("### 📁 المستندات")
        if st.session_state.documents:
            for doc in st.session_state.documents[:10]:
                st.markdown(f"""
                <div class="doc-item">
                    <div class="doc-info">
                        <div class="doc-icon">{doc['icon']}</div>
                        <div>
                            <div style="font-weight: 600;">{doc['name'][:20]}</div>
                            <div style="font-size: 0.8rem; color: #888;">{doc['chunks']} أجزاء</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لا توجد مستندات")
        
        st.markdown("---")
        
        # مسح الكل
        if st.button("🗑️ مسح الكل", use_container_width=True):
            st.session_state.documents = []
            st.session_state.messages = []
            if st.session_state.vector_store:
                st.session_state.vector_store.clear()
            st.success("تم المسح!")
            st.rerun()


def render_chat():
    """عرض المحادثة"""
    st.markdown("### 💬 اسأل المستندات")
    
    # حاوية المحادثة
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # رسائل الترحيب
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #888;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🤖</div>
            <h3>مرحباً! أنا مساعدك الذكي</h3>
            <p>ارفع بعض المستندات واسألني أي سؤال</p>
        </div>
        """, unsafe_allow_html=True)
    
    # عرض الرسائل
    for msg in st.session_state.messages:
        is_user = msg['role'] == 'user'
        
        avatar_class = "avatar-user" if is_user else "avatar-ai"
        avatar_icon = "👤" if is_user else "🤖"
        
        # بناء المصادر
        sources_html = ""
        if 'sources' in msg and msg['sources']:
            sources_html = """
            <div class="message-sources">
                <div class="sources-title">📚 المصادر:</div>
            """ + "".join([f"<div>• {s}</div>" for s in msg['sources']]) + """
            </div>
            """
        
        # الثقة
        confidence_html = ""
        if 'confidence' in msg:
            conf = msg['confidence']
            color = "#10b981" if conf > 70 else "#f59e0b" if conf > 40 else "#ef4444"
            confidence_html = f'<span style="font-size: 0.75rem; color: {color};">🎯 {conf}%</span>'
        
        st.markdown(f"""
        <div class="message {'user' if is_user else ''}">
            <div class="message-avatar {avatar_class}">{avatar_icon}</div>
            <div style="{'margin-left: auto;' if is_user else ''}">
                <div class="message-bubble">
                    {msg['content']}
                    {confidence_html}
                </div>
                {sources_html if not is_user else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # مؤشر الكتابة
    if st.session_state.get('show_typing', False):
        st.markdown("""
        <div class="message">
            <div class="message-avatar avatar-ai">🤖</div>
            <div class="message-bubble">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # مربع الإدخال
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    
    with col1:
        query = st.text_input(
            "message_input",
            placeholder="اكتب سؤالك هنا... 💭",
            label_visibility="collapsed"
        )
    
    with col2:
        send = st.button("إرسال 🚀", use_container_width=True)
    
    # معالجة الاستعلام
    if (send or query) and query:
        handle_query(query)


def handle_query(query):
    """معالجة الاستعلام"""
    # إضافة رسالة المستخدم
    st.session_state.messages.append({
        'role': 'user',
        'content': query
    })
    
    if st.session_state.vector_store and st.session_state.vector_store.documents:
        # عرض مؤشر الكتابة
        st.session_state.show_typing = True
        
        start_time = time.time()
        
        # البحث
        results = st.session_state.vector_store.search(
            query, 
            st.session_state.settings['top_k']
        )
        
        # توليد الرد
        engine = ChatEngine()
        response = engine.generate_response(query, results)
        
        response_time = time.time() - start_time
        
        # إضافة الرد
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response['answer'],
            'sources': response.get('sources', []),
            'confidence': response.get('confidence', 0)
        })
        
        # تحديث الإحصائيات
        st.session_state.stats['queries'] += 1
        st.session_state.stats['response_time'].append(response_time)
        
        st.session_state.show_typing = False
    else:
        st.session_state.messages.append({
            'role': 'assistant',
            'content': "📭 **لا توجد مستندات**\n\nيرجى رفع بعض المستندات أولاً للبدء في الاستعلام."
        })
    
    st.rerun()


def render_upload():
    """عرض قسم الرفع"""
    st.markdown("### 📤 رفع المستندات")
    
    uploaded_files = st.file_uploader(
        "اسحب وأفلت الملفات هنا",
        type=['pdf', 'docx', 'txt', 'csv', 'md'],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        process_files(uploaded_files)


def process_files(files):
    """معالجة الملفات"""
    processor = st.session_state.processor
    processor.chunk_size = st.session_state.settings['chunk_size']
    processor.chunk_overlap = st.session_state.settings['chunk_overlap']
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_chunks = []
    
    for i, file in enumerate(files):
        status_text.text(f"📄 جاري معالجة: {file.name}")
        
        try:
            # استخراج النص
            text = processor.extract_text(file)
            
            if not text.strip():
                st.warning(f"⚠️ الملف فارغ: {file.name}")
                continue
            
            # تقسيم النص
            chunks = processor.split_text(text, source=file.name)
            
            # حفظ معلومات المستند
            doc_info = {
                'name': file.name,
                'icon': processor.get_file_icon(file.name),
                'size': file.size,
                'chunks': len(chunks),
                'type': file.type
            }
            st.session_state.documents.append(doc_info)
            
            all_chunks.extend(chunks)
            
        except Exception as e:
            st.error(f"❌ خطأ في {file.name}: {str(e)}")
        
        progress_bar.progress((i + 1) / len(files))
    
    # بناء قاعدة البيانات
    if all_chunks:
        status_text.text("🔍 جاري بناء فهرس البحث...")
        
        if not st.session_state.vector_store:
            st.session_state.vector_store = VectorStore()
        
        st.session_state.vector_store.add_documents(all_chunks)
        
        st.success(f"✅ تم معالجة {len(files)} ملف ({len(all_chunks)} جزء)")
    
    status_text.empty()
    progress_bar.empty()
    st.rerun()


def render_analytics():
    """عرض التحليلات"""
    st.markdown("### 📊 لوحة التحليلات")
    
    # المقاييس
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.documents)}</div>
            <div class="metric-label">📄 المستندات</div>
        </div>
        """, unsafe_allow_html=True)
    
    total_chunks = 0
    if st.session_state.vector_store:
        total_chunks = st.session_state.vector_store.get_stats()['total_chunks']
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_chunks}</div>
            <div class="metric-label">📝 الأجزاء</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.stats['queries']}</div>
            <div class="metric-label">❓ الاستعلامات</div>
        </div>
        """, unsafe_allow_html=True)
    
    avg_time = 0
    if st.session_state.stats['response_time']:
        avg_time = sum(st.session_state.stats['response_time']) / len(st.session_state.stats['response_time'])
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_time:.1f}s</div>
            <div class="metric-label">⏱️ متوسط الوقت</div>
        </div>
        """, unsafe_allow_html=True)
    
    # معلومات النظام
    st.markdown("### ℹ️ معلومات النظام")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        - **numpy:** {'✅' if HAS_NUMPY else '❌'}
        - **sentence-transformers:** {'✅' if HAS_EMBEDDINGS else '❌'}
        - **PyPDF2:** {'✅' if HAS_PDF else '❌'}
        - **python-docx:** {'✅' if HAS_DOCX else '❌'}
        """)
    
    with col2:
        st.markdown(f"""
        - **Python:** {sys.version.split()[0]}
        - **Streamlit:** {st.__version__}
        - **نظام التشغيل:** {os.name}
        """)


# ═══════════════════════════════════════════════════════════
# الدالة الرئيسية
# ═══════════════════════════════════════════════════════════

def main():
    """الدالة الرئيسية"""
    # تحميل CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # تهيئة الجلسة
    init_session()
    
    # الهيدر
    render_header()
    render_features()
    
    # الشريط الجانبي
    render_sidebar()
    
    # التبويبات
    tab1, tab2, tab3 = st.tabs(["💬 المحادثة", "📤 رفع المستندات", "📊 التحليلات"])
    
    with tab1:
        render_chat()
    
    with tab2:
        render_upload()
        
        # عرض المستندات المحملة
        if st.session_state.documents:
            st.markdown("### 📋 المستندات المحملة")
            for doc in st.session_state.documents:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(f"{doc['icon']} {doc['name']}")
                with col2:
                    st.text(f"{doc['chunks']} أجزاء")
                with col3:
                    size_kb = doc['size'] / 1024
                    st.text(f"{size_kb:.1f} KB")
    
    with tab3:
        render_analytics()


# ═══════════════════════════════════════════════════════════
# التشغيل
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
