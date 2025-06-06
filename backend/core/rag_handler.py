import faiss
import numpy as np
import os
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.document import Document # Correct import
from langchain_community.llms import Ollama # Use Ollama wrapper from langchain
from langchain.chains import RetrievalQA

class RAGHandler:
    def __init__(self, embedder, ollama_model_name="mistral:instruct", ollama_base_url="http://localhost:11434"):
        """
        embedder: An instance of TextEmbedder.
        ollama_model_name: The name of the model served by Ollama (e.g., "mistral:instruct", "llama3:8b-instruct").
        ollama_base_url: The base URL for the Ollama API.
        """
        self.embedder = embedder # This is your SentenceTransformerEmbedder instance
        self.vector_stores = {} # Store FAISS indexes per doc_id: {doc_id: FAISS_store}
        
        # Custom embeddings wrapper for LangChain FAISS
        # LangChain's FAISS needs an Embeddings interface
        class LangchainSentenceTransformerEmbeddings:
            def __init__(self, st_embedder):
                self.st_embedder = st_embedder

            def embed_documents(self, texts):
                return self.st_embedder.get_embeddings(texts).tolist() # Ensure list of lists

            def embed_query(self, text):
                return self.st_embedder.get_embeddings([text])[0].tolist() # Ensure single list

        self.lc_embedder = LangchainSentenceTransformerEmbeddings(self.embedder)
        
        try:
            self.llm = Ollama(model=ollama_model_name, base_url=ollama_base_url)
            # Test connection, Ollama() instantiation itself doesn't guarantee connection.
            # A small test invoke:
            try:
                self.llm.invoke("Respond with 'Ok'") 
                print(f"Successfully connected to Ollama model '{ollama_model_name}' at {ollama_base_url}")
            except Exception as e:
                print(f"Warning: Could not confirm connection to Ollama model '{ollama_model_name}' during init: {e}")
                print("Ensure Ollama server is running and the model is pulled.")

        except Exception as e:
            print(f"Error initializing Ollama LLM: {e}")
            self.llm = None # Indicate LLM is not available

    def add_document_to_index(self, doc_id, chunks, faiss_index_path=None):
        """
        Creates or updates a FAISS index for a given document.
        If faiss_index_path is provided, it loads/saves from/to that path.
        Otherwise, it's an in-memory index for the session associated with doc_id.
        """
        if not chunks:
            print(f"No chunks provided for doc_id: {doc_id}")
            return

        # Convert text chunks to LangChain Document objects
        # We can add more metadata here if needed, like source chunk index
        lc_documents = [Document(page_content=chunk, metadata={"doc_id": doc_id, "chunk_idx": i}) for i, chunk in enumerate(chunks)]

        if faiss_index_path and os.path.exists(faiss_index_path):
            try:
                # FAISS.load_local requires allow_dangerous_deserialization=True for pickle
                self.vector_stores[doc_id] = FAISS.load_local(
                    folder_path=os.path.dirname(faiss_index_path), # LangChain expects folder_path
                    index_name=os.path.basename(faiss_index_path).replace(".faiss", ""), # and index_name
                    embeddings=self.lc_embedder,
                    allow_dangerous_deserialization=True 
                )
                print(f"Loaded existing FAISS index for {doc_id} from {faiss_index_path}")
                # Option: Add new documents to existing index if needed (FAISS.add_documents)
                # For simplicity now, we are overwriting or creating new.
                # If you want to merge, you'd load, then use self.vector_stores[doc_id].add_documents(lc_documents)
                # and then save again. Or, if we assume a full re-index:
                self.vector_stores[doc_id] = FAISS.from_documents(lc_documents, self.lc_embedder)
                self.vector_stores[doc_id].save_local(folder_path=os.path.dirname(faiss_index_path), index_name=os.path.basename(faiss_index_path).replace(".faiss", ""))

            except Exception as e:
                print(f"Error loading FAISS index for {doc_id} from {faiss_index_path}: {e}. Creating new one.")
                self.vector_stores[doc_id] = FAISS.from_documents(lc_documents, self.lc_embedder)
                if faiss_index_path:
                    self.vector_stores[doc_id].save_local(folder_path=os.path.dirname(faiss_index_path), index_name=os.path.basename(faiss_index_path).replace(".faiss", ""))

        else:
            self.vector_stores[doc_id] = FAISS.from_documents(lc_documents, self.lc_embedder)
            if faiss_index_path:
                 self.vector_stores[doc_id].save_local(folder_path=os.path.dirname(faiss_index_path), index_name=os.path.basename(faiss_index_path).replace(".faiss", ""))
            print(f"Created new FAISS index for {doc_id}.")
        
        if faiss_index_path:
             print(f"FAISS index for {doc_id} saved to {faiss_index_path}")


    def query(self, doc_id, query_text, faiss_index_path=None, k=3):
        """
        Queries the FAISS index for a given document using the Ollama LLM.
        """
        if self.llm is None:
            raise ConnectionError("Ollama LLM not initialized. Cannot perform query.")
            
        if doc_id not in self.vector_stores:
            if faiss_index_path and os.path.exists(faiss_index_path):
                print(f"Loading index for {doc_id} on demand for query.")
                try:
                    self.vector_stores[doc_id] = FAISS.load_local(
                        folder_path=os.path.dirname(faiss_index_path),
                        index_name=os.path.basename(faiss_index_path).replace(".faiss", ""),
                        embeddings=self.lc_embedder,
                        allow_dangerous_deserialization=True
                    )
                except Exception as e:
                    print(f"Failed to load FAISS index for {doc_id} at {faiss_index_path}: {e}")
                    raise FileNotFoundError(f"FAISS index for document {doc_id} not found or could not be loaded.")
            else:
                raise FileNotFoundError(f"FAISS index for document {doc_id} not loaded and path not provided.")

        current_vector_store = self.vector_stores[doc_id]
        retriever = current_vector_store.as_retriever(search_kwargs={"k": k})
        
        # Create a RetrievalQA chain
        # You can customize the chain_type (e.g., "stuff", "map_reduce", "refine")
        # "stuff" is simplest and works well for short contexts.
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff", # "stuff" puts all retrieved docs into the prompt.
                               # If context gets too long, Ollama/LLM might truncate or error.
                               # Consider "map_reduce" or "refine" for very large contexts.
            retriever=retriever,
            return_source_documents=True # To see which chunks were used
        )
        
        result = qa_chain.invoke({"query": query_text})
        
        answer = result['result']
        source_documents = result['source_documents']
        
        return answer, source_documents