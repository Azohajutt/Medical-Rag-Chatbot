# backend/ingest.py

import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import os

DATASET_PATH = "../data/dataset.xlsx"
CHROMA_PATH = "./chroma_db"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "medical_knowledge"


def load_excel_as_chunks(path: str) -> list[dict]:
    """
    Reads Excel file and converts each row into clean text chunks.
    Works with any column structure.
    """
    print(f"📄 Reading {path} ...")

    df = pd.read_excel(path, engine="openpyxl")
    df.dropna(how="all", inplace=True)

    print(f"✅ Found {len(df)} rows | Columns: {list(df.columns)}")

    chunks = []

    for i, row in df.iterrows():
        parts = []

        for col in df.columns:
            val = row[col]

            if pd.notna(val):
                val_str = str(val).strip()
                if val_str:
                    parts.append(f"{col}: {val_str}")

        if parts:
            text = "\n".join(parts)

            chunks.append({
                "id": f"row_{i}",
                "text": text,
                # 🚀 FIXED: NO FILE NAME LEAK ANYMORE
                "source": "medical_knowledge_base"
            })

    print(f"✅ Created {len(chunks)} clean chunks.")
    return chunks


def ingest():
    chunks = load_excel_as_chunks(DATASET_PATH)

    if not chunks:
        print("❌ No data found in dataset.")
        return

    print(f"\n🔢 Loading embedding model: {EMBED_MODEL_NAME}")
    model = SentenceTransformer(EMBED_MODEL_NAME)

    texts = [c["text"] for c in chunks]

    print(f"⚡ Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32
    ).tolist()

    print("\n💾 Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # 🚀 SAFE RESET (prevents duplicates)
    try:
        client.delete_collection(COLLECTION_NAME)
        print("🔄 Old collection deleted.")
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # 🚀 Batch insert
    batch_size = 100

    for start in range(0, len(chunks), batch_size):
        batch_chunks = chunks[start:start + batch_size]
        batch_embeddings = embeddings[start:start + batch_size]

        collection.add(
            documents=[c["text"] for c in batch_chunks],
            embeddings=batch_embeddings,
            ids=[c["id"] for c in batch_chunks],
            metadatas=[{"source": c["source"]} for c in batch_chunks]
        )

        print(f"📦 Stored {start} → {start + len(batch_chunks)}")

    print("\n✅ Ingestion complete!")
    print(f"📂 ChromaDB path: {CHROMA_PATH}")
    print(f"📊 Total chunks stored: {len(chunks)}")


if __name__ == "__main__":
    ingest()