from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import faiss
import pickle
import os
import json
import asyncio
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: SentenceTransformers import failed: {e}")
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from rag_pipeline import answer_query, answer_query_streaming, client
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
    
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        print("❌ SentenceTransformers not available. Cannot load models.")
        assets_loaded = False
    elif os.path.exists(INDEX_PATH) and os.path.exists(SENTENCES_PATH):
        print("🚀 Loading models and data...")
        try:
            # Use CPU for Hugging Face Spaces (no GPU guaranteed)
            embedding_model = SentenceTransformer(MODEL_NAME, device='cpu')
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

# Enable CORS for all origins (for Hugging Face Spaces)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for HF Spaces
    allow_credentials=False,  # Set to False for public deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

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
            # Stream the response
            async for chunk in answer_query_streaming(
                query=request.message,
                embedding_model=embedding_model,
                index=index,
                sentences=sentences,
                client=client,
                top_k=5
            ):
                # Add small chunks for better streaming effect
                if len(chunk) > 10:
                    # Split longer chunks into smaller pieces
                    words = chunk.split(' ')
                    for i in range(0, len(words), 2):  # 2 words at a time
                        word_chunk = ' '.join(words[i:i+2])
                        if word_chunk.strip():
                            yield f"data: {json.dumps({'chunk': word_chunk + ' ', 'done': False})}\n\n"
                            await asyncio.sleep(0.05)  # 50ms delay for smoother streaming
                else:
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                    await asyncio.sleep(0.03)  # 30ms delay
            
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
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

# Serve static files FIRST (for assets like JS, CSS, images)
if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve React app for non-asset routes
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str = ""):
    """Serve React app for any path that doesn't match API routes or assets"""
    # Skip serving HTML for asset requests (they should be handled by StaticFiles above)
    if full_path.startswith("assets/") or full_path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Let API routes handle themselves
    if full_path.startswith("chat") or full_path.startswith("health") or full_path.startswith("docs") or full_path.startswith("openapi"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve React app's index.html for all other routes (including root)
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    else:
        return {"message": "SRB RAG Chatbot API is running!", "status": "healthy", "note": "Frontend not available - static/index.html not found"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))  # HF Spaces uses port 7860
    uvicorn.run(app, host="0.0.0.0", port=port)
