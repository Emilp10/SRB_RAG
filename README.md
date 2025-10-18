# SRB RAG Chatbot with Modern React Frontend

A sophisticated Retrieval-Augmented Generation (RAG) chatbot that answers questions about the Student Resource Book (SRB) using advanced NLP techniques and a beautiful modern React frontend.

## 🚀 Features

- **Modern React Frontend**: Beautiful, responsive UI built with React, TypeScript, and Tailwind CSS
- **FastAPI Backend**: High-performance API with automatic documentation
- **RAG Pipeline**: Advanced retrieval-augmented generation using FAISS and sentence transformers  
- **Semantic Search**: Find relevant information using vector similarity search
- **Real-time Chat**: Instant responses with typing indicators
- **Document Intelligence**: Powered by Google's Generative AI (Gemini 2.5 Flash)

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/JSON    ┌──────────────────┐    RAG Pipeline    ┌─────────────────┐
│  React Frontend │ ──────────────> │  FastAPI Backend │ ─────────────────> │  AI Models      │
│  (Port 5173)    │                 │  (Port 8000)     │                    │  FAISS + Gemini │
└─────────────────┘                 └──────────────────┘                    └─────────────────┘
```

## 📁 Project Structure

```
RAG_proj/
├── backend_api.py              # FastAPI backend server
├── rag_pipeline.py             # Core RAG logic
├── preprocess.py               # Data preprocessing
├── requirements.txt            # Python dependencies
├── faiss_index.bin            # Pre-built FAISS index (LFS)
├── sentences.pkl              # Processed sentences (LFS)
├── start_chatbot.bat          # Windows startup script
├── start_chatbot.sh           # Linux/Mac startup script
└── lovable-project/           # React frontend
    ├── src/
    │   ├── components/        # React components
    │   ├── pages/            # Page components
    │   └── ...
    ├── package.json          # Node.js dependencies
    └── ...
```

## 🚦 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install frontend dependencies:**
```bash
cd lovable-project
npm install
```

3. **Set up environment variables:**
Create a `.env` file with your Google API key:
```env
GEMINI_API_KEY=your_google_api_key_here
```

4. **Run preprocessing (first time only):**
```bash
python preprocess.py
```

### Running the Application

#### Option 1: Use startup scripts (Recommended)
**Windows:**
```bash
start_chatbot.bat
```

**Linux/Mac:**
```bash
chmod +x start_chatbot.sh
./start_chatbot.sh
```

#### Option 2: Manual startup
**Terminal 1 - Backend:**
```bash
python backend_api.py
```

**Terminal 2 - Frontend:**
```bash
cd lovable-project
npm run dev
```

### Access the Application
- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🎨 Frontend Features

- **Modern Design**: Dark theme with purple/indigo gradients
- **Glassmorphism Effects**: Backdrop blur and ambient lighting
- **Smooth Animations**: Fade-in messages and hover effects
- **Responsive Layout**: Works on desktop and mobile
- **Real-time Typing**: Shows when AI is processing
- **Message History**: Scroll through conversation
- **Clear Chat**: Reset conversation anytime

## 🤖 API Endpoints

### POST /chat
Send a message to the chatbot
```json
{
  "message": "What attendance do I need to maintain?"
}
```

Response:
```json
{
  "response": "According to the SRB...",
  "status": "success"
}
```

### GET /health
Check if models are loaded
```json
{
  "status": "healthy",
  "models_loaded": true
}
```

## 🔧 Technical Details

### Backend Stack
- **FastAPI**: Modern Python web framework
- **FAISS**: Vector similarity search
- **SentenceTransformers**: Text embeddings
- **Google Generative AI**: Response generation
- **Uvicorn**: ASGI server

### Frontend Stack
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling
- **Vite**: Build tool and dev server
- **Radix UI**: Accessible components
- **Lucide React**: Icons

### AI Pipeline
1. **Document Processing**: PDF → Text chunks
2. **Embedding**: Text → Vector representations
3. **Indexing**: Vectors → FAISS search index
4. **Query Processing**: User question → Query embedding
5. **Retrieval**: Find similar document chunks
6. **Generation**: AI generates contextual response

## 🚀 Deployment

### Development
Already configured for local development with hot reload.

### Production
1. Build the frontend:
```bash
cd lovable-project
npm run build
```

2. Serve with a production ASGI server:
```bash
pip install gunicorn
gunicorn backend_api:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with love using modern web technologies
- Powered by Google's Generative AI
- UI components from Radix UI and shadcn/ui
- Vector search powered by Facebook's FAISS