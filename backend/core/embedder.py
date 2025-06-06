from sentence_transformers import SentenceTransformer
import numpy as np

class TextEmbedder:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initializes the SentenceTransformer model.
        'all-MiniLM-L6-v2' is small and fast.
        'all-mpnet-base-v2' is larger but offers better quality.
        """
        try:
            self.model = SentenceTransformer(model_name)
            print(f"SentenceTransformer model '{model_name}' loaded successfully.")
        except Exception as e:
            print(f"Error loading SentenceTransformer model '{model_name}': {e}")
            print("Please ensure you have a working internet connection to download the model,")
            print("or that the model is available locally.")
            # You might want to raise the exception or handle it more gracefully
            # depending on whether the application can run without the embedder.
            raise

    def get_embeddings(self, texts):
        """
        Generates embeddings for a list of texts.
        texts: A list of strings.
        Returns: A numpy array of embeddings.
        """
        if not isinstance(texts, list):
            texts = [texts]
        return self.model.encode(texts, convert_to_tensor=False) # Returns numpy array

    def get_embedding_dimension(self):
        """Returns the dimension of the embeddings."""
        # Encode a dummy sentence to get the dimension
        dummy_embedding = self.model.encode("test")
        return len(dummy_embedding)