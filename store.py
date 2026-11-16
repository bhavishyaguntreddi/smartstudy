# store.py - save chunks in ChromaDB and search them
import chromadb
from ingest import build_chunks

client = chromadb.PersistentClient(path="chroma_db")  # saves to the chroma_db folder
collection = client.get_or_create_collection("notes")  # one table for all chunks

def add_file(path):
    """Chunk a file and store it. upsert means re-adding never makes duplicates."""
    records = build_chunks(path)
    collection.upsert(
        ids=[r["id"] for r in records],
        documents=[r["text"] for r in records],  # ChromaDB embeds these for us
        metadatas=[{"source": r["source"], "page": r["page"], "topic": r["topic"]}
                   for r in records],            # kept for citations and topic filters
    )
    return len(records)

def search(question, n_results=3, topic=None):
    """Return the closest chunks to the question, with their source and distance."""
    where = {"topic": topic} if topic else None  # optional: search one topic only
    res = collection.query(query_texts=[question], n_results=n_results, where=where)
    return [
        {"text": d, "source": m["source"], "page": m["page"],
         "topic": m["topic"], "distance": dist}
        for d, m, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]

if __name__ == "__main__":  # quick test: python store.py
    from pathlib import Path
    for f in Path("sample_notes").glob("*.txt"):
        print(f.name, "stored", add_file(f), "chunks")
    for q in ["Where does photosynthesis happen in a plant cell?",
              "What happens to price when there is a surplus?",
              "What do mitochondria do?"]:   # this last one is NOT in the notes
        print("\nQ:", q)
        for r in search(q):
            print(f"  {r['distance']:.3f} | {r['source']} | {r['text'][:70]}...")