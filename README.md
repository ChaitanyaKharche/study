#CogniMap Studio 🧠✨
Transform your documents into interactive, queryable mind maps using local AI.

CogniMap Studio is designed to run entirely on your own machine, making it perfect for private study and for users with limited VRAM (e.g., 8GB). It uses the power of Ollama to turn dense materials into visual, easy-to-explore learning tools.

A mind map generated from a document.

## Features
📚 Upload Your Documents: Works seamlessly with PDF and TXT files.

🗺️ Auto-Generate Mind Maps: Automatically extracts key concepts and their relationships to build a visual map of your material.

✍️ Interact & Explore: A fully interactive and editable mind map powered by Cytoscape.js.

💬 Ask Your Documents Anything: Use a built-in RAG pipeline to chat with your materials, getting answers from a local LLM without your data ever leaving your computer.

## Tech Stack
Category	Technologies
Backend	Python, Flask, LangChain
Frontend	React, Cytoscape.js, Axios
AI/ML	Ollama, FAISS (CPU), Sentence-Transformers
Models	all-MiniLM-L6-v2 (Embeddings), mistral:instruct / llama3:8b (LLM)

Export to Sheets
## Getting Started
Follow these steps to get CogniMap Studio running on your local machine.

### 1. Prerequisites
Make sure you have the following installed:

Git: To clone the repository.

Python 3.9+: For the backend server.

Node.js & npm: For the frontend application.

Ollama: Install from the official Ollama website.

### 2. Clone the Repository
Bash

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
### 3. Set Up Ollama & AI Models
First, ensure the Ollama server is running. Then, pull the LLM you want to use. mistral:instruct is recommended for systems with 8GB VRAM.

Bash

# Recommended for 8GB VRAM
ollama pull mistral:instruct

# A more capable alternative
ollama pull llama3:8b-instruct
### 4. Set Up the Backend
Open a terminal in the project's root directory.

Bash

# Navigate to the backend folder
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
### 5. Set Up the Frontend
Open a second terminal in the project's root directory.

Bash

# Navigate to the frontend folder
cd frontend

# Install Node.js dependencies
npm install
### 6. Launch the Application!
You'll need both terminals running simultaneously.

In your first terminal (backend):

Bash

# Make sure you are in the backend/ directory with venv active
flask run
The backend will be available at http://127.0.0.1:5000.

In your second terminal (frontend):

Bash

# Make sure you are in the frontend/ directory
npm start
The application will open in your browser at http://localhost:3000.

## For Developers
### Experimentation with JupyterLab
If you want to experiment with the backend logic (document parsing, embedding, etc.), you can use JupyterLab.

Bash

# Install JupyterLab in the backend's virtual environment
pip install jupyterlab

# Start the server
jupyter lab
### Hugging Face Token
Ollama handles the model downloads, so a Hugging Face token is generally not required to run this application. However, if you plan to modify the code to download models directly from the Hub, you can log in via the terminal:

Bash

pip install huggingface_hub
huggingface-cli login
