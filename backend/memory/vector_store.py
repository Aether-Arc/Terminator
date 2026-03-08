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