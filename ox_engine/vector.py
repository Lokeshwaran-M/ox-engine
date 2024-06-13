from sentence_transformers import SentenceTransformer
import numpy as np


class Vector:
    def __init__(self) -> None:
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def set_model(self, md_name):
        self.model = SentenceTransformer(md_name)

    def encode(self, data):
        embeddings = self.model.encode(data, convert_to_numpy=True).tolist()
        return embeddings

    @classmethod
    def sim(cls, veca, vecb, sim_format=1):
        """
        Calculates similarity between two vectors based on the specified format.

        Args:
            veca: First vector.
            vecb: Second vector.
            sim_format: Integer specifying the similarity metric.
                1: Euclidean Distance
                2: Cosine Similarity
                3: Dot Product (default)

        Returns:
            The similarity value based on the chosen format.
        """
     
        veca = np.array(veca).flatten()
        vecb = np.array(vecb).flatten()

        if sim_format == 1:
            # Euclidean Distance
            euclidean_distance = np.linalg.norm(veca - vecb)
            return euclidean_distance
        elif sim_format == 2:
            # Cosine Similarity
            cosine_similarity = np.dot(veca, vecb) / (
                np.linalg.norm(veca) * np.linalg.norm(vecb)
            )
            return cosine_similarity
        else:
            # Dot Product (default)
            dot_product = np.dot(veca, vecb)
            return dot_product
