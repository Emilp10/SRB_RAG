import gradio as gr
import asyncio
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import uvicorn
import os
import sys

# Import your existing RAG pipeline
try:
    from rag_pipeline import answer_query_streaming, answer_query
    from app_hf import *  # Import all the setup from app_hf
    HAS_RAG = True
except ImportError:
    HAS_RAG = False
    print("RAG pipeline not available, using mock responses")

async def chat_with_streaming(message, history):
    """Gradio-compatible chat function with streaming"""
    if not HAS_RAG:
        # Mock response for testing
        response = "I'm sorry, the RAG pipeline is not available. This is a test response."
        for i in range(0, len(response), 3):
            yield response[:i+3]
            await asyncio.sleep(0.1)
        return
    
    try:
        # Use your existing streaming function
        full_response = ""
        async for chunk in answer_query_streaming(
            query=message,
            embedding_model=embedding_model,
            index=index,
            sentences=sentences,
            client=client,
            top_k=5
        ):
            full_response += chunk
            yield full_response
    except Exception as e:
        yield f"Sorry, I encountered an error: {str(e)}"

# Create Gradio interface
with gr.Blocks(
    title="🤖 SRB RAG Chatbot",
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="blue"
    ),
    css="""
    .gradio-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .chat-message {
        border-radius: 15px;
        padding: 12px;
        margin: 8px 0;
    }
    """
) as demo:
    
    gr.HTML("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: white; margin-bottom: 10px;">🤖 SRB RAG Chatbot</h1>
        <p style="color: rgba(255,255,255,0.8);">Ask questions about the Student Resource Book (SRB)</p>
    </div>
    """)
    
    # Main chat interface
    chatbot = gr.Chatbot(
        height=400,
        bubble_full_width=False,
        show_label=False,
        container=True,
        elem_classes="chat-message"
    )
    
    msg = gr.Textbox(
        placeholder="Ask me anything about the Student Resource Book...",
        show_label=False,
        container=False
    )
    
    # Example questions
    with gr.Row():
        gr.Examples(
            examples=[
                "What attendance do I need to maintain?",
                "What happens if I use unfair means in an exam?",
                "Explain the grading and evaluation criteria",
                "What are the library borrowing limits?",
                "Tell me about examination rules and procedures",
                "What are the medical leave policies?"
            ],
            inputs=msg,
            label="💡 Try these questions:"
        )
    
    # Clear button
    clear = gr.Button("🗑️ Clear Chat", variant="secondary")
    
    # Event handlers
    msg.submit(
        chat_with_streaming, 
        inputs=[msg, chatbot], 
        outputs=chatbot
    ).then(
        lambda: "", 
        outputs=msg
    )
    
    clear.click(lambda: None, outputs=chatbot)

# Launch configuration
if __name__ == "__main__":
    # For HF Spaces
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
