"""
Build the ChromaDB vector database from finance_tips.txt.
Run this ONCE before starting the chatbot: python rag_setup/build_finance_db.py
"""

from pathlib import Path
import chromadb


def build_finance_database():
    script_dir = Path(__file__).parent
    data_path = script_dir.parent / "data" / "finance_tips.txt"
    chroma_path = script_dir.parent / "chroma"

    with open(data_path, "r", encoding="utf-8") as f:
        content = f.read()

    documents = [doc.strip() for doc in content.split("\n\n---\n\n") if doc.strip()]

    client = chromadb.PersistentClient(path=str(chroma_path))

    try:
        client.delete_collection("finance_db")
        print("Deleted existing finance_db collection.")
    except Exception:
        pass

    collection = client.create_collection("finance_db")
    collection.add(
        documents=documents,
        ids=[f"tip_{i}" for i in range(len(documents))],
    )

    print(f"Created finance_db with {len(documents)} documents in {chroma_path}")


if __name__ == "__main__":
    build_finance_database()
