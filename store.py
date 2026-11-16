# store.py - save chunks in ChromaDB and search them.
# Each visitor gets a PRIVATE collection named after their session_id, so notes are never shared.
import chromadb
from ingest import build_chunks

client = chromadb.PersistentClient(path="chroma_db")  # saves to the chroma_db folder

def get_collection(session_id):
    """This visitor's own collection (created on first use)."""
    return client.get_or_create_collection(f"notes_{session_id}")

def add_file(path, session_id):
    """Chunk a file and store it in this visitor's collection. upsert never makes duplicates."""
    records = build_chunks(path)
    get_collection(session_id).upsert(
        ids=[r["id"] for r in records],
        documents=[r["text"] for r in records],  # ChromaDB embeds these for us
        metadatas=[{"source": r["source"], "page": r["page"], "topic": r["topic"]}
                   for r in records],            # kept for citations and topic filters
    )
    return len(records)

def search(question, session_id, n_results=3, topic=None):
    """Return the closest chunks from THIS visitor's notes, with source and distance."""
    col = get_collection(session_id)
    if col.count() == 0:
        return []                                 # nothing uploaded yet
    where = {"topic": topic} if topic else None   # optional: search one topic only
    res = col.query(query_texts=[question], n_results=min(n_results, col.count()), where=where)
    return [
        {"text": d, "source": m["source"], "page": m["page"],
         "topic": m["topic"], "distance": dist}
        for d, m, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]

def delete_all(session_id):
    """Delete everything stored for this visitor (the My data page will use this)."""
    try:
        client.delete_collection(f"notes_{session_id}")
    except Exception:
        pass   # nothing to delete

if __name__ == "__main__":   # privacy test: python store.py
    delete_all("visitor_a"); delete_all("visitor_b")
    add_file("sample_notes/photosynthesis.txt", "visitor_a")
    add_file("sample_notes/supply_and_demand.txt", "visitor_b")
    for sid in ["visitor_a", "visitor_b"]:
        topics = sorted({m["topic"] for m in get_collection(sid).get()["metadatas"]})
        print(sid, "sees topics:", topics)
    hits = search("What happens to price when there is a surplus?", "visitor_a")
    print("visitor_a searching for 'surplus' only sees:", sorted({h["source"] for h in hits}))
    delete_all("visitor_a"); delete_all("visitor_b")
    print("after delete, visitor_a has", get_collection("visitor_a").count(), "chunks")
    delete_all("visitor_a")   # tidy up the empty collection that line just made