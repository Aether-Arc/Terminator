import chromadb

client = chromadb.Client()

collection = client.get_or_create_collection("event_memory")


def store_memory(text):

    collection.add(
        documents=[text],
        ids=[str(hash(text))]
    )


def search_memory(query):

    return collection.query(
        query_texts=[query],
        n_results=3
    )

# MOCK VECTOR STORE - Replaced chromadb to avoid Rust build errors

# We will just store memories in a simple Python list for the demo
# mock_collection = []

# def store_memory(text):
#     print(f"[*] MOCK VECTOR STORE: Saving memory -> {text[:50]}...")
#     mock_collection.append(text)

# def search_memory(query):
#     print(f"[*] MOCK VECTOR STORE: Searching for -> {query}")
    
#     # If we have memories, return the most recent ones. Otherwise, return a default response.
#     # The return format mimics what ChromaDB would normally output.
#     if mock_collection:
#         # Return up to the last 3 memories
#         return {"documents": [mock_collection[-3:]]} 
#     else:
#         return {"documents": [["No past event memories found. Starting fresh."]]}