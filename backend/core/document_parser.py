import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize
import os
import shutil # For removing directory if needed
import re

# --- NLTK Data Path and Punkt Download (More Aggressive Control) ---
# Define a specific path for NLTK data WITHIN your project's backend directory
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Gets path to 'backend'
PROJECT_NLTK_DATA_DIR = os.path.join(backend_dir, 'nltk_data_local')

print(f"Ensuring NLTK data directory exists at: {PROJECT_NLTK_DATA_DIR}")
if not os.path.exists(PROJECT_NLTK_DATA_DIR):
    os.makedirs(PROJECT_NLTK_DATA_DIR)

# Force NLTK to primarily (or only) look in this directory for this session
# This helps isolate from any system-wide or user-wide corrupted nltk_data
print(f"Original NLTK data path: {nltk.data.path}")
if PROJECT_NLTK_DATA_DIR not in nltk.data.path:
    nltk.data.path.insert(0, PROJECT_NLTK_DATA_DIR)
print(f"Modified NLTK data path (prioritizing local): {nltk.data.path}")

# For an even more aggressive approach, uncomment the next line to ONLY use this path:
# nltk.data.path = [PROJECT_NLTK_DATA_DIR]
# print(f"Aggressively set NLTK data path to: {nltk.data.path}")

# Check for 'punkt' in our specific directory and download if necessary
PUNKT_RESOURCE_PATH = 'tokenizers/punkt/PY3/english.pickle'
PUNKT_LOCAL_FULL_PATH_CHECK = os.path.join(PROJECT_NLTK_DATA_DIR, 'tokenizers', 'punkt', 'PY3', 'english.pickle')
PUNKT_DIR_TO_DELETE = os.path.join(PROJECT_NLTK_DATA_DIR, 'tokenizers', 'punkt')


# This function attempts to find or download punkt specifically to our project's nltk_data_local
def ensure_punkt_is_available():
    try:
        # Check if the specific file exists in our controlled path
        if os.path.exists(PUNKT_LOCAL_FULL_PATH_CHECK):
            # Verify NLTK can find it using its own mechanisms within this path
            nltk.data.find(PUNKT_RESOURCE_PATH, paths=[PROJECT_NLTK_DATA_DIR])
            print(f"NLTK 'punkt/english.pickle' resource found and verified in {PROJECT_NLTK_DATA_DIR}.")
            return True
        else:
            raise LookupError("Local punkt pickle not found at initial check.")
    except LookupError:
        print(f"NLTK 'punkt' not found in {PROJECT_NLTK_DATA_DIR}. Attempting download to this location...")
        
        # Clean up any potentially corrupted 'punkt' dir in our local path before download
        if os.path.exists(PUNKT_DIR_TO_DELETE):
            print(f"Removing existing (potentially corrupt) punkt directory: {PUNKT_DIR_TO_DELETE}")
            try:
                shutil.rmtree(PUNKT_DIR_TO_DELETE)
            except Exception as e_rm:
                print(f"Could not remove existing punkt directory: {e_rm}")
                # Continue anyway, download might overwrite or fail gracefully

        try:
            nltk.download('punkt', download_dir=PROJECT_NLTK_DATA_DIR)
            # Verify again after download by checking the file directly
            if os.path.exists(PUNKT_LOCAL_FULL_PATH_CHECK):
                 nltk.data.find(PUNKT_RESOURCE_PATH, paths=[PROJECT_NLTK_DATA_DIR]) # Final check
                 print(f"NLTK 'punkt' downloaded and verified successfully to {PROJECT_NLTK_DATA_DIR}.")
                 return True
            else:
                print(f"NLTK 'punkt' download reported success, but {PUNKT_LOCAL_FULL_PATH_CHECK} not found.")
                return False
        except Exception as e_download:
            print(f"Failed to download 'punkt' to {PROJECT_NLTK_DATA_DIR}: {e_download}")
            return False

# Call the function to ensure punkt is ready before any parsing happens
if not ensure_punkt_is_available():
    # If punkt is still not available after all attempts, this is a critical failure.
    # The application might not function correctly.
    print("CRITICAL: NLTK 'punkt' resource could not be made available. Sentence tokenization will likely fail.")
    # Depending on how critical, you might raise an error here to stop the app from starting
    # raise RuntimeError("NLTK 'punkt' resource could not be initialized.")

def clean_text(text):
    """Basic text cleaning."""
    # Replace multiple spaces/newlines with a single space
    text = re.sub(r'\s+', ' ', text)
    # You could add more cleaning here if needed, e.g., for specific non-standard chars
    # For now, let's keep it simple.
    return text.strip()

def parse_pdf(filepath):
    """Parses a PDF file and extracts text chunks (sentences)."""
    chunks = []
    metadata = {"source": filepath}
    try:
        doc = fitz.open(filepath)
        full_text_list = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            full_text_list.append(page.get_text("text"))
        doc.close()
        
        full_text = "\n".join(full_text_list) # Join pages with newline
        full_text = clean_text(full_text) # Apply basic cleaning

        if full_text:
            # --- Diagnostic: Test with a simple string first ---
            try:
                print("Attempting to tokenize a simple test string...")
                test_text = "This is a simple test sentence. This is another one to ensure punkt is working."
                test_sentences = sent_tokenize(test_text, language='english')
                print(f"Test tokenization successful: {len(test_sentences)} sentences found in test.")
            except Exception as e_test_tokenize:
                print(f"CRITICAL ERROR: Failed to tokenize even a simple test string: {e_test_tokenize}")
                # If this fails, NLTK/Punkt installation is fundamentally broken
                raise RuntimeError(f"NLTK sent_tokenize failed on basic test: {e_test_tokenize}") from e_test_tokenize
            # --- End Diagnostic ---

            try:
                # Now tokenize the actual document content
                sentences = sent_tokenize(full_text, language='english')
            except Exception as e_tokenize:
                print(f"Error during sent_tokenize on actual document content: {e_tokenize}")
                print(f"This might indicate an issue with the 'punkt' data or specific text patterns.")
                print(f"Content snippet being tokenized (first 300 chars after cleaning): {full_text[:300]}")
                
                # Fallback: If sent_tokenize fails, treat the whole cleaned text as one chunk,
                # or split by newline as a very basic fallback. This is not ideal for sentence chunking.
                print("Fallback: Treating paragraphs (split by double newlines if any, or whole text) as chunks due to tokenization error.")
                # Before cleaning, newlines were more significant. After cleaning, they are single spaces.
                # Let's just use the full_text as one chunk if sent_tokenize fails.
                # A better fallback would be to split by paragraph if possible before cleaning fully.
                # For now, to prevent empty chunks if this specific error occurs:
                if full_text:
                    chunks.append(full_text) # Add the whole text as one chunk if tokenization fails
                if not chunks: # If full_text was empty or became empty
                    raise ValueError("Document parsing resulted in no text or failed at sentence tokenization.") from e_tokenize
                return chunks, metadata # Return with the fallback chunk

            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    chunks.append(sentence.strip())
            
            if not chunks: # If after tokenization, still no chunks (e.g., text was only whitespace)
                raise ValueError("Document contains no usable text after tokenization.")
        else: # If full_text was empty after extraction and cleaning
            raise ValueError("Document contains no extractable text.")
            
        return chunks, metadata
    except Exception as e:
        print(f"Error parsing PDF {filepath}: {e}")
        raise


def parse_txt(filepath):
    """Parses a TXT file and extracts text chunks (sentences)."""
    chunks = []
    metadata = {"source": filepath}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            full_text = f.read()
        full_text = clean_text(full_text)

        if full_text:
            # --- Diagnostic: Test with a simple string first ---
            try:
                print("Attempting to tokenize a simple test string (TXT)...")
                test_text = "This is a simple test sentence. This is another one."
                test_sentences = sent_tokenize(test_text, language='english')
                print(f"Test tokenization successful (TXT): {len(test_sentences)} sentences found.")
            except Exception as e_test_tokenize:
                print(f"CRITICAL ERROR (TXT): Failed to tokenize simple test string: {e_test_tokenize}")
                raise RuntimeError(f"NLTK sent_tokenize failed on basic test (TXT): {e_test_tokenize}") from e_test_tokenize
            # --- End Diagnostic ---
            
            try:
                sentences = sent_tokenize(full_text, language='english')
            except Exception as e_tokenize:
                print(f"Error during sent_tokenize on actual TXT content: {e_tokenize}")
                print(f"Content snippet (TXT) (first 300 chars after cleaning): {full_text[:300]}")
                if full_text:
                    chunks.append(full_text)
                if not chunks:
                    raise ValueError("TXT Document parsing resulted in no text or failed at sentence tokenization.") from e_tokenize
                return chunks, metadata

            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    chunks.append(sentence.strip())
            if not chunks:
                raise ValueError("TXT Document contains no usable text after tokenization.")
        else:
            raise ValueError("TXT Document contains no extractable text.")
        return chunks, metadata
    except Exception as e:
        print(f"Error parsing TXT {filepath}: {e}")
        raise

def parse_document(filepath):
    """Generic document parser based on file extension."""
    if filepath.lower().endswith(".pdf"):
        return parse_pdf(filepath)
    elif filepath.lower().endswith(".txt"):
        return parse_txt(filepath)
    else:
        raise ValueError(f"Unsupported file type: {filepath}")