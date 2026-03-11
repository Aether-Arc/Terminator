# MOCK VECTOR STORE - Bypassing chromadb to avoid Rust build errors
# This is perfect for the hackathon as it keeps everything running in RAM

mock_collection = []

def store_memory(text):
    print(f"[*] VECTOR STORE: Saving memory -> {text[:50]}...")
    mock_collection.append(text)

def search_memory(query):
    print(f"[*] VECTOR STORE: Searching for -> {query}")
    
    # If we have memories, return the most recent ones. 
    # The return format mimics what ChromaDB would normally output for LangChain.
    if mock_collection:
        # Return up to the last 3 memories
        return {"documents": [mock_collection[-3:]]} 
    else:
        return {"documents": [["No past event memories found. Starting fresh."]]}