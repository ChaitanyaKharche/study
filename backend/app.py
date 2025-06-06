import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from werkzeug.utils import secure_filename

from core.document_parser import parse_document
from core.embedder import TextEmbedder
from core.graph_generator import GraphGenerator
from core.rag_handler import RAGHandler
from utils.helpers import ensure_dir

# Configuration
UPLOAD_FOLDER = os.path.join('data', 'uploads')
FAISS_INDEX_FOLDER = os.path.join('data', 'faiss_indexes')
MIND_MAP_FOLDER = os.path.join('data', 'mind_maps')
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

# Ensure data directories exist
ensure_dir(UPLOAD_FOLDER)
ensure_dir(FAISS_INDEX_FOLDER)
ensure_dir(MIND_MAP_FOLDER)

app = Flask(__name__)
CORS(app) # Enable CORS for all routes and origins by default for development
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Initialize components ---
# It's better to initialize these once, especially models,
# but be mindful of memory usage if models are large.
# For Ollama-based RAG, the main memory hog (LLM) is external.
text_embedder = TextEmbedder() # Uses sentence-transformers/all-MiniLM-L6-v2
graph_generator = GraphGenerator(text_embedder)
rag_handler = RAGHandler(text_embedder) # RAG will use Ollama

# --- Helper Function ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- API Endpoints ---
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        doc_id = filename.rsplit('.', 1)[0] # Use filename without extension as doc_id

        try:
            # 1. Parse document
            chunks, metadata = parse_document(filepath)
            if not chunks:
                return jsonify({"error": "Could not parse document or no text found"}), 500

            # 2. Create/Update FAISS index for this document
            faiss_index_path = os.path.join(FAISS_INDEX_FOLDER, f"{doc_id}.faiss")
            rag_handler.add_document_to_index(doc_id, chunks, faiss_index_path)
            
            # 3. Generate Mind Map
            # For MVP, we generate graph from all chunks of the document.
            # A more advanced version might select key chunks or summarize.
            mind_map_data = graph_generator.create_graph_from_chunks(chunks, doc_id)
            
            # Save mind map data
            mind_map_file_path = os.path.join(MIND_MAP_FOLDER, f"{doc_id}.json")
            with open(mind_map_file_path, 'w') as f:
                json.dump(mind_map_data, f)

            return jsonify({
                "message": "File processed successfully",
                "doc_id": doc_id,
                "filename": filename,
                "mind_map_data": mind_map_data
            }), 200
        except Exception as e:
            app.logger.error(f"Error processing file {filename}: {e}")
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
    else:
        return jsonify({"error": "File type not allowed"}), 400

@app.route('/api/mindmap/<doc_id>', methods=['GET'])
def get_mindmap(doc_id):
    mind_map_file_path = os.path.join(MIND_MAP_FOLDER, f"{doc_id}.json")
    try:
        with open(mind_map_file_path, 'r') as f:
            mind_map_data = json.load(f)
        return jsonify(mind_map_data), 200
    except FileNotFoundError:
        return jsonify({"error": "Mind map not found for this document"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/query/<doc_id>', methods=['POST'])
def query_document(doc_id):
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Query not provided"}), 400
    
    query_text = data['query']
    faiss_index_path = os.path.join(FAISS_INDEX_FOLDER, f"{doc_id}.faiss")

    if not os.path.exists(faiss_index_path):
        return jsonify({"error": "Document index not found. Please upload and process the document first."}), 404

    try:
        answer, sources = rag_handler.query(doc_id, query_text, faiss_index_path)
        return jsonify({"answer": answer, "sources": [s.page_content for s in sources]}), 200 # Send source text
    except Exception as e:
        app.logger.error(f"Error querying document {doc_id}: {e}")
        # More specific error handling for Ollama connection issues
        if "Connection refused" in str(e) or "Failed to connect" in str(e) :
             return jsonify({"error": "Could not connect to Ollama. Is Ollama running?"}), 503
        return jsonify({"error": f"Error during query processing: {str(e)}"}), 500

if __name__ == '__main__':
    # For development, debug=True is fine. For production, use a proper WSGI server like Gunicorn.
    app.run(debug=True, host='0.0.0.0', port=5000)