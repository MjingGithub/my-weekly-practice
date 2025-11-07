## 向量数据库chromadb使用 https://www.trychroma.com/
import chromadb
# Create a Chroma Client
client = chromadb.HttpClient(host='localhost', port=8000)
client.reset()
# Create a collection
collection = client.create_collection("sample_collection")
# Add docs to the collection. Can also update and delete. Row-based API coming soon!
collection.add(
    documents=["This is document1", "This is document2"], # we embed for you, or bring your own
    metadatas=[{"source": "notion"}, {"source": "google-docs"}], # filter on arbitrary metadata!
    ids=["doc1", "doc2"], # must be unique for each doc
)
# Query the collection
results = collection.query(
    query_texts=["This is a query document"], # Chroma will embed this for you
    n_results=2, # # how many results to return
    # where={"metadata_field": "is_equal_to_this"}, # optional filter
    # where_document={"$contains":"search_string"}  # optional filter
)
print(results)

