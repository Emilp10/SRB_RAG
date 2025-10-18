import os
import requests
import fitz  # PyMuPDF
from tqdm.auto import tqdm
from spacy.lang.en import English
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def text_formatter(text: str) -> str:
    """Performs minor formatting on text."""
    cleaned_text = text.replace("\n", " ").strip()
    return cleaned_text


def open_and_read_pdf(pdf_path: str) -> list[dict]:
    """Reads PDF pages into a structured list of dicts."""
    doc = fitz.open(pdf_path)
    pages_and_texts = []
    for page_number, page in tqdm(enumerate(doc), total=len(doc), desc="Reading PDF"):
        text = page.get_text()
        text = text_formatter(text)
        pages_and_texts.append({
            "page_number": page_number - 3,
            "page_char_count": len(text),
            "page_word_count": len(text.split(" ")),
            "page_sentence_count_raw": len(text.split(". ")),
            "page_token_count": len(text) / 4,
            "text": text
        })
    return pages_and_texts


def sentence_splitter(pages_and_texts, chunk_size=5):
    nlp = English()
    nlp.add_pipe("sentencizer")
    chunks = []

    for item in tqdm(pages_and_texts, desc="Splitting into sentence chunks"):
        doc = nlp(item["text"])
        sents = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        
        for i in range(0, len(sents), chunk_size):
            chunk = " ".join(sents[i:i + chunk_size])
            chunks.append({
                "page_number": item["page_number"],
                "sentence_chunk": chunk
            })

    return chunks


def build_faiss_index(sentences, model_name="all-mpnet-base-v2"):
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    sentence_texts = [s["sentence_chunk"] for s in sentences]
    embeddings = model.encode(sentence_texts, convert_to_tensor=False, show_progress_bar=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    print(f"FAISS index built with {index.ntotal} embeddings.")
    return model, index, sentence_texts


def generate_answer(client, context_text, query):
    prompt = f"""Based on the following context items, please answer the query.
    Give yourself room to think by extracting relevant passages from the context before answering the query.
    Don't return the thinking, only return the answer.
    Make sure your answers are as explanatory as possible.\n\nContext:\n{context_text}\n\nQuestion: {query}"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction="Provide a clear, relevant, and factual answer using the given context. Don't speak about the context, just use it to answer the question. If the users query is irrelevant to the context like 'count numbers from 1 to 10', respond with 'I'm sorry, I can't assist with that.'",
            temperature=0.2,
        )
    )
    return response.text


async def generate_answer_streaming(client, context_text, query):
    """Generate streaming answer using Gemini API"""
    prompt = f"""Based on the following context items, please answer the query.
    Give yourself room to think by extracting relevant passages from the context before answering the query.
    Don't return the thinking, only return the answer.
    Make sure your answers are as explanatory as possible.\n\nContext:\n{context_text}\n\nQuestion: {query}"""
    
    # Use streaming generation
    response_stream = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction="Provide a clear, relevant, and factual answer using the given context. Don't speak about the context, just use it to answer the question. If the users query is irrelevant to the context like 'count numbers from 1 to 10', respond with 'I'm sorry, I can't assist with that.'",
            temperature=0.2,
        )
    )
    
    for chunk in response_stream:
        if hasattr(chunk, 'text') and chunk.text:
            yield chunk.text


def answer_query(query, embedding_model, index, sentences, client, top_k=5):
    query_embedding = embedding_model.encode([query])[0]
    distances, indices = index.search(np.array([query_embedding]), top_k)
    retrieved_sentences = [sentences[i] for i in indices[0]]

    context_text = "\n".join(retrieved_sentences)
    answer = generate_answer(client, context_text, query)
    return answer


async def answer_query_streaming(query, embedding_model, index, sentences, client, top_k=5):
    """Streaming version of answer_query"""
    query_embedding = embedding_model.encode([query])[0]
    distances, indices = index.search(np.array([query_embedding]), top_k)
    retrieved_sentences = [sentences[i] for i in indices[0]]

    context_text = "\n".join(retrieved_sentences)
    
    async for chunk in generate_answer_streaming(client, context_text, query):
        yield chunk


def load_models(pdf_path="SRB-2025.pdf"):
    if not os.path.exists(pdf_path):
        print("Downloading SRB PDF...")
        url = "https://engineering.nmims.edu/wp-content/uploads/2025/09/SRB-2025-1.pdf"
        response = requests.get(url)
        if response.status_code == 200:
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            print("Download complete.")
        else:
            print("Failed to download PDF.")
    
    # Process PDF
    pages_and_texts = open_and_read_pdf(pdf_path)
    sentences = sentence_splitter(pages_and_texts)
    
    # Build FAISS index
    embedding_model, index, sentence_texts = build_faiss_index(sentences)
    return embedding_model, index, sentence_texts, client
