import gradio as gr
import asyncio
import time

def chat_with_streaming(message, history):
    """Simple chat function with mock streaming for HF Spaces"""
    
    # Mock responses based on common questions
    responses = {
        "attendance": "According to the SRB, students must maintain a minimum of 75% attendance in each subject to be eligible for examinations. Medical leave may be considered for attendance calculations with proper documentation.",
        "examination": "The SRB outlines that examinations follow a structured schedule. Students must carry valid ID cards, arrive 15 minutes before the exam, and strictly follow examination protocols. Any unfair means will result in penalties.",
        "grading": "The grading system follows a 10-point scale with specific criteria for each grade. Continuous assessment includes assignments, quizzes, and practical work contributing to the final grade.",
        "library": "Library borrowing limits are set based on student category. Regular students can borrow up to 5 books for 14 days, while research students have extended privileges.",
        "unfair means": "Use of unfair means in examinations is strictly prohibited and results in serious consequences including cancellation of the examination, suspension, or other disciplinary actions as per university rules."
    }
    
    # Simple keyword matching for demo
    message_lower = message.lower()
    response = "I'm sorry, I couldn't find specific information about that in the Student Resource Book. Please try asking about attendance, examinations, grading, library policies, or examination rules."
    
    for keyword, ans in responses.items():
        if keyword in message_lower:
            response = ans
            break
    
    # Simulate streaming
    full_response = ""
    words = response.split()
    
    for i, word in enumerate(words):
        full_response += word + " "
        time.sleep(0.05)  # Small delay to simulate streaming
        yield full_response

# Create Gradio interface with beautiful styling
with gr.Blocks(
    title="🤖 SRB RAG Chatbot",
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="blue",
        neutral_hue="slate"
    ),
    css="""
    .gradio-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    .main-header {
        text-align: center;
        padding: 30px 20px;
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    .chat-container {
        background: rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    """
) as demo:
    
    with gr.Column(elem_classes="main-content"):
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1 style="color: white; margin-bottom: 15px; font-size: 2.5em;">🤖 SRB RAG Chatbot</h1>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.2em; margin: 0;">
                Your AI assistant for Student Resource Book queries
            </p>
            <p style="color: rgba(255,255,255,0.7); margin-top: 10px;">
                Ask questions about attendance, examinations, grading, and academic policies
            </p>
        </div>
        """)
        
        with gr.Column(elem_classes="chat-container"):
            # Main chat interface
            chatbot = gr.Chatbot(
                height=500,
                bubble_full_width=False,
                show_label=False,
                container=True,
                show_copy_button=True,
                avatar_images=[None, "🤖"]
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Ask me anything about the Student Resource Book...",
                    show_label=False,
                    container=False,
                    scale=4
                )
                submit_btn = gr.Button("Send", variant="primary", scale=1)
            
            # Example questions
            with gr.Row():
                with gr.Column():
                    gr.Examples(
                        examples=[
                            "What attendance do I need to maintain?",
                            "What happens if I use unfair means in an exam?",
                            "Explain the grading and evaluation criteria"
                        ],
                        inputs=msg,
                        label="💡 Quick Questions:"
                    )
                with gr.Column():
                    gr.Examples(
                        examples=[
                            "What are the library borrowing limits?",
                            "Tell me about examination rules and procedures",
                            "What are the medical leave policies?"
                        ],
                        inputs=msg,
                        label="📚 More Topics:"
                    )
            
            # Clear button
            clear = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")
    
    # Event handlers
    def respond(message, history):
        if not message.strip():
            return history, ""
            
        # Add user message to history
        history = history or []
        history.append([message, None])
        
        # Generate streaming response
        bot_response = ""
        for partial_response in chat_with_streaming(message, history):
            history[-1][1] = partial_response
            yield history, ""
        
        return history, ""
    
    msg.submit(respond, inputs=[msg, chatbot], outputs=[chatbot, msg])
    submit_btn.click(respond, inputs=[msg, chatbot], outputs=[chatbot, msg])
    clear.click(lambda: ([], ""), outputs=[chatbot, msg])

# Launch for HF Spaces
if __name__ == "__main__":
    demo.launch()
