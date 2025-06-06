import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import uuid # For generating unique node IDs

class GraphGenerator:
    def __init__(self, embedder, similarity_threshold=0.65):
        """
        embedder: An instance of TextEmbedder.
        similarity_threshold: Threshold for creating edges between nodes.
        """
        self.embedder = embedder
        self.similarity_threshold = similarity_threshold

    def create_graph_from_chunks(self, chunks, doc_id, max_nodes=50, max_edges_per_node=3):
        """
        Creates a graph structure (nodes and edges) from text chunks.
        For MVP, nodes are the chunks themselves. Edges are based on semantic similarity.

        Args:
            chunks (list of str): The text chunks from the document.
            doc_id (str): Identifier for the document.
            max_nodes (int): Max number of nodes to include (prioritize longer chunks).
            max_edges_per_node (int): Max outgoing edges from any node (for clarity).


        Returns:
            dict: A dictionary with 'nodes' and 'edges' lists, suitable for Cytoscape.js.
        """
        if not chunks:
            return {"nodes": [], "edges": []}

        # Prioritize longer chunks for better node representation if too many chunks
        if len(chunks) > max_nodes:
            sorted_chunks = sorted(chunks, key=len, reverse=True)
            selected_chunks = sorted_chunks[:max_nodes]
        else:
            selected_chunks = chunks

        if not selected_chunks:
            return {"nodes": [], "edges": []}
            
        embeddings = self.embedder.get_embeddings(selected_chunks)
        
        nodes = []
        for i, chunk_text in enumerate(selected_chunks):
            # For Cytoscape, each node needs an 'id' and 'label'
            # Keep label short for better display, use first N words/chars.
            label = chunk_text[:75] + "..." if len(chunk_text) > 75 else chunk_text
            nodes.append({
                "data": {
                    "id": f"{doc_id}_node_{i}_{uuid.uuid4().hex[:4]}", # More unique ID
                    "label": label,
                    "full_text": chunk_text, # Store full text for potential display on click
                    "doc_id": doc_id
                }
            })

        edges = []
        # Calculate cosine similarity matrix
        # FAISS is for retrieval, direct cosine similarity is fine for graph building on selected_chunks
        if len(embeddings) > 1:
            sim_matrix = cosine_similarity(embeddings)
            
            for i in range(len(selected_chunks)):
                # Get top N similar nodes, excluding self
                similar_indices = np.argsort(sim_matrix[i])[::-1]
                edge_count_for_node_i = 0
                for j_idx in similar_indices:
                    if i == j_idx:
                        continue # Skip self-similarity
                    
                    # Check if an edge in the other direction already exists (for undirected feel)
                    # This check is basic and might not be perfect for complex graphs.
                    edge_exists = any(
                        (edge['data']['source'] == nodes[j_idx]['data']['id'] and edge['data']['target'] == nodes[i]['data']['id'])
                        for edge in edges
                    )
                    if edge_exists:
                        continue

                    similarity_score = sim_matrix[i][j_idx]
                    if similarity_score > self.similarity_threshold and edge_count_for_node_i < max_edges_per_node:
                        edges.append({
                            "data": {
                                "id": f"edge_{nodes[i]['data']['id']}_{nodes[j_idx]['data']['id']}_{uuid.uuid4().hex[:4]}",
                                "source": nodes[i]['data']['id'],
                                "target": nodes[j_idx]['data']['id'],
                                "weight": float(similarity_score) # Cytoscape can use weight
                            }
                        })
                        edge_count_for_node_i +=1


        return {"nodes": nodes, "edges": edges}