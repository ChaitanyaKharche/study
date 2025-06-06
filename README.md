# CogniMap Studio - AI-Powered Mind Map Learning Environment

CogniMap Studio helps you transform your course materials into interactive mind maps and query them using local AI models. This project is an MVP designed for users with limited VRAM (e.g., 8GB), leveraging Ollama for serving LLMs.

## Features (MVP)

* Upload PDF and TXT documents.
* Generate a basic mind map based on semantic chunks and their relationships.
* Interactive mind map visualization using Cytoscape.js.
* Query your documents using a RAG (Retrieval Augmented Generation) pipeline with a local LLM.

## Tech Stack

* **Backend:** Python, Flask, Sentence-Transformers, FAISS-cpu, LangChain (for RAG), Ollama (for LLM)
* **Frontend:** React, Cytoscape.js, Axios
* **AI Models:**
    * Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
    * LLM for Q&A: Served via Ollama (e.g., `mistral:instruct`, `llama3:8b-instruct`)

## Prerequisites

1.  **Python 3.9+**
2.  **Node.js and npm/yarn**
3.  **Ollama:** Install from [https://ollama.com/](https://ollama.com/)
4.  **Pull an LLM model via Ollama:**
    * Open your terminal and run:
        ```bash
        ollama pull mistral:instruct
        # OR for a slightly more capable model (might be slower on 8GB VRAM)
        ollama pull llama3:8b-instruct
        ```
    * Ensure Ollama is running (usually it starts a background server). By default, it serves on `http://localhost:11434`.

## Setup

### Backend

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `data` directory if it doesn't exist:
    ```bash
    mkdir -p data/uploads data/faiss_indexes data/mind_maps
    ```

### Frontend

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install Node.js dependencies:
    ```bash
    npm install
    # OR
    yarn install
    ```

## Running the Application

1.  **Start Ollama (if not already running):** Usually, Ollama runs as a background service after installation. Verify it's accessible (e.g., by visiting `http://localhost:11434` in your browser or using `ollama list`).

2.  **Start the Backend Server:**
    * Open a terminal, navigate to the `backend` directory, activate the virtual environment.
    * Run the Flask app:
        ```bash
        flask run
        ```
    * It should start on `http://127.0.0.1:5000` by default.

3.  **Start the Frontend Development Server:**
    * Open another terminal, navigate to the `frontend` directory.
    * Run the React app:
        ```bash
        npm start
        # OR
        yarn start
        ```
    * This will usually open the app in your browser at `http://localhost:3000`.

## Hugging Face Token

If you need to download models directly using the `transformers` or `sentence-transformers` library for tasks not handled by Ollama, or if you encounter download issues for specific models:

1.  Log in using the Hugging Face CLI (install it with `pip install huggingface_hub`):
    ```bash
    huggingface-cli login
    ```
    Paste your token (``) when prompted.
2.  Alternatively, set it as an environment variable:
    ```bash
    export HUGGING_FACE_HUB_TOKEN=""
    ```
    For Ollama usage with default models, the token is generally not required.

## JupyterLab for Experimentation

You can use JupyterLab to test parts of the backend logic:
1.  Install JupyterLab in your backend's virtual environment: `pip install jupyterlab`
2.  Run: `jupyter lab`
3.  Create notebooks to experiment with `document_parser.py`, `embedder.py`, `graph_generator.py` logic before full integration.