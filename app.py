# app.py
import gradio as gr
import faiss
import pickle
import os
import time
from sentence_transformers import SentenceTransformer
from rag_pipeline import answer_query, client

# ------------------ 1. CONFIG ------------------
INDEX_PATH = "faiss_index.bin"
SENTENCES_PATH = "sentences.pkl"
MODEL_NAME = "all-mpnet-base-v2"

embedding_model, index, sentences = None, None, None
assets_loaded = False

if os.path.exists(INDEX_PATH) and os.path.exists(SENTENCES_PATH):
    print("🚀 Loading models and data...")
    embedding_model = SentenceTransformer(MODEL_NAME)
    index = faiss.read_index(INDEX_PATH)
    with open(SENTENCES_PATH, "rb") as f:
        sentences = pickle.load(f)
    assets_loaded = True
    print("✅ Assets ready.")
else:
    print("⚠️ Preprocessed files not found. Run preprocess.py first.")

# ------------------ 2. CLEAN, COMPACT STYLING ------------------
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');

* { font-family: 'Outfit', sans-serif; box-sizing: border-box; }

body, html {
  margin: 0;
  padding: 0;
  background: #0f172a;
  color: #E2E8F0;
  height: 100%;
  overflow-y: auto;
}

/* Container */
.gradio-container {
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  color: #E2E8F0;
}

/* Header */
#header {
  text-align: center;
  padding: 24px 0 18px;
  background: rgba(255,255,255,0.05);
  border-bottom: 1px solid rgba(255,255,255,0.08);
  border-radius: 0 0 12px 12px;
  box-shadow: 0 3px 10px rgba(0,0,0,0.3);
}
#header img {
  width: 120px;
  margin-bottom: 8px;
}
#header h1 {
  color: #60A5FA;
  font-size: 2rem;
  margin: 0;
}
#header p {
  color: #94A3B8;
  font-size: 1rem;
  margin-top: 6px;
}

/* Chatbot */
#chatbot {
  margin: 20px auto;
  width: 80%;
  max-width: 950px;
  height: 500px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  box-shadow: 0 6px 24px rgba(0,0,0,0.4);
  overflow-y: auto;
  padding: 10px;
}

/* Message Bubbles */
#chatbot .message-bubble {
  border-radius: 14px !important;
  padding: 10px 14px !important;
  font-size: 1rem;
  line-height: 1.45;
  animation: fadeIn 0.3s ease;
}
.user-message {
  background: linear-gradient(135deg, #2563EB, #60A5FA) !important;
  color: white !important;
}
.bot-message {
  background: rgba(255,255,255,0.07) !important;
  color: #E2E8F0 !important;
  border: 1px solid rgba(255,255,255,0.1);
}

@keyframes fadeIn {
  from {opacity: 0; transform: translateY(4px);}
  to {opacity: 1; transform: translateY(0);}
}

/* Input and Button */
.input-row {
  width: 80%;
  max-width: 950px;
  margin: 0 auto 12px auto;
  display: flex;
  align-items: center;
  gap: 8px;
}
.gr-textbox textarea {
  background: rgba(255,255,255,0.08) !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
  border-radius: 12px !important;
  color: #F8FAFC !important;
  font-size: 0.95rem;
}
.gr-textbox textarea:focus {
  border-color: #60A5FA !important;
  box-shadow: 0 0 0 3px rgba(96,165,250,0.25);
}
.gr-button {
  border-radius: 10px !important;
  background: linear-gradient(135deg, #3B82F6, #06B6D4) !important;
  color: white !important;
  font-weight: 600 !important;
  height: 42px !important;
  transition: all 0.2s ease;
}
.gr-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(96,165,250,0.4);
}

/* Examples */
#examples {
  width: 80%;
  max-width: 950px;
  margin: 0 auto 30px auto;
  text-align: center;
}
#examples .gradio-button {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  color: #E2E8F0;
  font-size: 0.9rem;
  padding: 6px 14px;
  transition: all 0.2s;
}
#examples .gradio-button:hover {
  background: linear-gradient(135deg, #3B82F6, #06B6D4);
  color: white;
}
"""

# ------------------ 3. CHAT FUNCTION ------------------
def respond(message, chat_history):
    if not assets_loaded:
        bot_message = "⚠️ Assets not loaded. Please run preprocess.py and restart."
        chat_history.append((message, bot_message))
        return "", chat_history

    try:
        answer = answer_query(
            query=message,
            embedding_model=embedding_model,
            index=index,
            sentences=sentences,
            client=client
        )
        chat_history.append((message, ""))
        for i in range(len(answer)):
            time.sleep(0.01)
            chat_history[-1] = (message, answer[: i+1])
            yield "", chat_history
    except Exception as e:
        chat_history.append((message, f"⚠️ Error: {str(e)}"))
        yield "", chat_history

# ------------------ 4. GRADIO APP ------------------
with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as demo:
    if not assets_loaded:
        gr.Markdown("## ❌ Error: Missing assets. Please run `python preprocess.py` first.")
    else:
        with gr.Row(elem_id="header"):
            gr.HTML("""
                <h1>MPSTME SRB Chatbot</h1>
                <p>Ask anything from the Student Resource Book (SRB)</p>
            """)

        chatbot = gr.Chatbot(
            elem_id="chatbot",
            height=500,  # comfortable height
            avatar_images=(None, "bot_avatar.png")
        )

        with gr.Row(elem_classes="input-row"):
            txt_input = gr.Textbox(
                show_label=False,
                placeholder="💭 Type your question...",
                container=False,
                scale=7
            )
            submit_btn = gr.Button("Ask ➤", variant="primary", scale=1)

        with gr.Row(elem_id="examples"):
            gr.Examples(
                examples=[
                    "Explain the attendance rules.",
                    "What are the medical leave policies?",
                    "Summarize the grading and evaluation criteria.",
                    "What are the library borrowing limits?"
                ],
                inputs=txt_input,
                label="💡 Try asking:"
            )

        submit_btn.click(respond, [txt_input, chatbot], [txt_input, chatbot])
        txt_input.submit(respond, [txt_input, chatbot], [txt_input, chatbot])

# ------------------ 5. LAUNCH ------------------
if __name__ == "__main__":
    demo.launch()
