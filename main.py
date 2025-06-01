import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from ollama_embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from tqdm import tqdm
from transformers_llm import TransformersLLM  # our custom wrapper

# --- CONFIGURATION ---
FILE_PATH = "scraped-output.txt"
MODEL_NAME = "Qwen/Qwen2.5-Coder-3B-Instruct"  # using the old model

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# --- LOAD & SPLIT DOCUMENTS ---
print("Loading document(s)...")
loader = TextLoader(FILE_PATH, encoding="utf8")
documents = loader.load()

print("Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(documents)
print(f"Total chunks before filtering: {len(docs)}")

filtered_docs = [doc for doc in docs if len(doc.page_content.strip()) > 50]
print(f"Chunks after filtering (length > 50): {len(filtered_docs)}")

# --- EMBEDDING & VECTOR STORE ---
print("Computing embeddings for each chunk (this may take a while)...")
embeddings = OllamaEmbeddings()  # uses your local Ollama API for embeddings

embeddings_list = []
doc_texts = []
for doc in tqdm(filtered_docs, desc="Embedding chunks"):
    text = doc.page_content.strip()
    doc_texts.append(text)
    embedding = embeddings.embed_query(text)
    embeddings_list.append(embedding)

print("Building FAISS vector store from computed embeddings...")
text_embeddings = list(zip(doc_texts, embeddings_list))
vectorstore = FAISS.from_embeddings(text_embeddings, embeddings)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# --- SET UP GPU-ENABLED LLM & RETRIEVAL QA CHAIN ---
print("Initializing GPU-enabled LLM for generation...")
llm = TransformersLLM(model_name=MODEL_NAME, max_new_tokens=200)
print("Setting up RetrievalQA chain...")

# Create a proper PromptTemplate object.
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "Answer the question concisely based on the context below.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    )
)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt_template}
)

print("Setup complete. You can now ask questions. Type 'quit' to exit.\n")
while True:
    query = input("Enter your question (or 'quit'): ")
    if query.lower().strip() == "quit":
        break
    answer = qa.run(query)
    print("\nAnswer:", answer, "\n")
