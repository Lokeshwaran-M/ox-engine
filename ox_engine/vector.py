from sentence_transformers import SentenceTransformer



class vector:
    def __init__(self) -> None:
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    def set_model(self,md_name):
        self.model = SentenceTransformer(md_name)

    def encode(self,data):
        embeddings = self.model.encode(data)
        return embeddings
    

