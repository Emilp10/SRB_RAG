import faiss
import pickle
from rag_pipeline import open_and_read_pdf, sentence_splitter, build_faiss_index

PDF_PATH = "SRB-2025.pdf"  
INDEX_SAVE_PATH = "faiss_index.bin"
SENTENCES_SAVE_PATH = "sentences.pkl"

if __name__ == "__main__":
    print("--- Starting Pre-processing ---")

    pages_and_texts = open_and_read_pdf(pdf_path=PDF_PATH)
    sentence_chunks = sentence_splitter(pages_and_texts)

    embedding_model, index, sentence_texts = build_faiss_index(sentence_chunks)

    print(f"Saving FAISS index to '{INDEX_SAVE_PATH}'...")
    faiss.write_index(index, INDEX_SAVE_PATH)

    print(f"Saving sentence chunks to '{SENTENCES_SAVE_PATH}'...")
    with open(SENTENCES_SAVE_PATH, "wb") as f:
        pickle.dump(sentence_texts, f)

    print("\n✅ Pre-processing complete!")
    print(f"You can now run the main application with 'python app.py'")