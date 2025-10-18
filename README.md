---
title: SRB RAG Chatbot
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 🤖 SRB RAG Chatbot

A sophisticated **Retrieval-Augmented Generation (RAG) chatbot** that answers questions about the **Student Resource Book (SRB)** using advanced NLP techniques. Features real-time streaming responses and a beautiful modern UI.

## 🚀 Features

- **🔄 Real-time Streaming**: Responses appear progressively like ChatGPT
- **🎯 Advanced RAG Pipeline**: FAISS vector search + Google Gemini 2.5 Flash
- **🎨 Beautiful UI**: Modern React frontend with purple glassmorphism design
- **📚 Semantic Search**: Find relevant information using vector similarity
- **💬 Interactive Chat**: Example questions and typing indicators
- **📱 Responsive**: Works perfectly on mobile and desktop

## 💡 Try These Questions

- **"What attendance do I need to maintain?"**
- **"What happens if I use unfair means in an exam?"** 
- **"Explain the grading and evaluation criteria"**
- **"What are the library borrowing limits?"**
- **"Tell me about examination rules and procedures"**
- **"What are the medical leave policies?"**

## 🤖 How It Works

1. **📄 Document Processing**: SRB PDF → Text chunks → Vector embeddings
2. **🔍 Query Processing**: Your question → Query embedding  
3. **🎯 Retrieval**: Find most relevant document sections using FAISS
4. **🤖 Generation**: AI generates contextual response using retrieved context
5. **⚡ Streaming**: Response streams back word-by-word for smooth experience

## 🛠️ Technology Stack

- **Backend**: FastAPI + Python
- **AI Models**: Google Gemini 2.5 Flash + SentenceTransformers
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Frontend**: React + TypeScript + Tailwind CSS
- **Deployment**: Docker + Hugging Face Spaces

## 📊 Architecture

```
User Query → Embedding → FAISS Search → Context Retrieval → AI Generation → Streaming Response
```

## 🎨 UI Features

- **🌟 Modern Design**: Dark theme with purple gradients
- **⚡ Real-time Streaming**: Watch responses appear progressively  
- **📱 Mobile-First**: Responsive design that works everywhere
- **✨ Smooth Animations**: Beautiful transitions and effects
- **💬 Chat History**: Keep track of your conversation
- **🎯 Example Questions**: Click to try predefined questions

## 🔧 Technical Details

- **Embeddings**: all-MiniLM-L6-v2 (SentenceTransformers)
- **Vector Search**: FAISS with cosine similarity
- **Language Model**: Google Gemini 2.5 Flash
- **Streaming**: Server-Sent Events for real-time responses
- **Deployment**: Optimized for CPU-only inference

## 📞 Support

Built with ❤️ using modern AI and web technologies. 

**GitHub**: [View Source Code](https://github.com/yourusername/srb-rag-chatbot)

---

**🚀 Ready to explore? Ask any question about the Student Resource Book!**
