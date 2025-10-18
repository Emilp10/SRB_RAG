from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import faiss
import pickle
import os
import json
import asyncio
from sentence_transformers import SentenceTransformer
from rag_pipeline import answer_query, client
import uvicorn

# Global variables for models
embedding_model = None
index = None
sentences = None
assets_loaded = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models
    global embedding_model, index, sentences, assets_loaded
    
    INDEX_PATH = "faiss_index.bin"
    SENTENCES_PATH = "sentences.pkl"
    MODEL_NAME = "all-mpnet-base-v2"
    
    if os.path.exists(INDEX_PATH) and os.path.exists(SENTENCES_PATH):
        print("🚀 Loading models and data...")
        try:
            embedding_model = SentenceTransformer(MODEL_NAME)
            index = faiss.read_index(INDEX_PATH)
            with open(SENTENCES_PATH, "rb") as f:
                sentences = pickle.load(f)
            assets_loaded = True
            print("✅ Assets ready.")
        except Exception as e:
            print(f"❌ Error loading assets: {e}")
            assets_loaded = False
    else:
        print("⚠️ Preprocessed files not found. Run preprocess.py first.")
        assets_loaded = False
    
    yield
    
    # Shutdown: cleanup if needed
    print("🔄 Shutting down...")

app = FastAPI(title="SRB RAG Chatbot API", lifespan=lifespan)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str = "success"



@app.get("/")
async def root():
    return {"message": "SRB RAG Chatbot API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if assets_loaded else "unhealthy",
        "models_loaded": assets_loaded
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not assets_loaded:
        raise HTTPException(
            status_code=503, 
            detail="Models not loaded. Please check if preprocessed files exist."
        )
    
    try:
        # Use the existing RAG pipeline
        response = answer_query(
            query=request.message,
            embedding_model=embedding_model,
            index=index,
            sentences=sentences,
            client=client,
            top_k=5
        )
        
        return ChatResponse(response=response, status="success")
    
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing your question: {str(e)}")

@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    if not assets_loaded:
        raise HTTPException(
            status_code=503, 
            detail="Models not loaded. Please check if preprocessed files exist."
        )
    
    async def generate_response():
        try:
            # Get relevant context using RAG pipeline
            from rag_pipeline import answer_query_streaming
            
            # Stream the response
            async for chunk in answer_query_streaming(
                query=request.message,
                embedding_model=embedding_model,
                index=index,
                sentences=sentences,
                client=client,
                top_k=5
            ):
                yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
            
            # Signal completion
            yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
            
        except Exception as e:
            print(f"Error in streaming: {e}")
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # For nginx
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
