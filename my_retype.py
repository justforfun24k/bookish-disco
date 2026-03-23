import chromadb
class VectorMemory:
    def __init__(self,persist_dir="vector_memory"):
        from chromadb.config import Settings
        try:
            self.client=chromadb.Client(Settings(
                persist_directory=persist_dir,
                anonymized_telemetry=False
            ))
            self.collection=self.client.create_collection(name="memory")
            self.embeddings=[]

        except Exception as e:
            print(f"Vector memory error: {e}")
            self.client=None
            self.collection=None

    def _simple_embedding(self,text):
        import hashlib
        embedding=[0]*10
        for i,char in enumerate(text[:10]):
            embedding[i%10]=ord(char)
        magnitude=sum(x**2 for x in embedding)**0.5
        if magnitude>0:
            embedding=[x/magnitude for x in embedding]
        return embedding

    def add(self,text,metadata=None):
        if not self.collection:
            return False
        try:
            embedding=self._simple_embedding(text)
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                ids=[f"memory_{len(self.embeddings)}"]
            )
            self.embeddings.append(text)
            return True
        except Exception as e:
            print(f"Add error: {e}")
            return False
    
    def search(self,query,n_results=3):
        if not self.collection:
            return []
        try:
            query_embedding=self._simple_embedding(query)
            results=self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            return results.get('documents',[[]])[0]
        except Exception as e:
            print(f"Search error: {e}")
            return []

class PiAgentWithMemory:
    def __init__(self):
        self.session=Session()

    def chat(self,message):
