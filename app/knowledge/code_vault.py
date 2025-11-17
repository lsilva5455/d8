"""
Code Vault - RAG System for Legacy Code Retrieval
Vector-based semantic search with metadata filtering
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import json
import logging
from sentence_transformers import SentenceTransformer

from app.utils.code_ingestor import CodeFragment, CodeIngestor

logger = logging.getLogger(__name__)


class CodeVault:
    """
    RAG system for legacy code
    Stores code fragments as vectors and retrieves relevant ones semantically
    """
    
    def __init__(self, 
                 persist_directory: str = "./data/code_vault",
                 collection_name: str = "legacy_code",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize Code Vault with ChromaDB
        
        Args:
            persist_directory: Where to store the vector database
            collection_name: Name of the collection
            embedding_model: SentenceTransformer model for embeddings
        """
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Legacy code fragments for RAG"}
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        logger.info(f"✅ Code Vault initialized: {collection_name}")
        logger.info(f"📊 Current fragments in vault: {self.collection.count()}")
    
    def ingest_fragments(self, fragments: List[CodeFragment]) -> None:
        """
        Ingest code fragments into the vault
        
        Args:
            fragments: List of CodeFragment objects to store
        """
        if not fragments:
            logger.warning("No fragments to ingest")
            return
        
        logger.info(f"📥 Ingesting {len(fragments)} code fragments...")
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for fragment in fragments:
            # Create rich document text for embedding
            doc_text = self._create_document_text(fragment)
            documents.append(doc_text)
            
            # Prepare metadata (ChromaDB requires flat dict)
            metadata = {
                "type": fragment.type,
                "name": fragment.name,
                "file_path": fragment.file_path,
                "line_start": fragment.line_start,
                "line_end": fragment.line_end,
                "platform": fragment.metadata.get('platform', 'unknown'),
                "action": fragment.metadata.get('action', 'unknown'),
                "has_docstring": fragment.docstring is not None,
                "source_code": fragment.source_code,  # Store full code
                "signature": fragment.signature
            }
            metadatas.append(metadata)
            ids.append(fragment.hash)
        
        # Add to collection in batches (ChromaDB limit is ~40k per batch)
        batch_size = 5000
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            self.collection.add(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids
            )
            
            logger.info(f"✅ Batch {i//batch_size + 1} ingested ({len(batch_docs)} fragments)")
        
        logger.info(f"✅ Ingestion complete! Total fragments: {self.collection.count()}")
    
    def _create_document_text(self, fragment: CodeFragment) -> str:
        """
        Create rich text representation of code fragment for embedding
        Combines name, signature, docstring, and metadata for better retrieval
        """
        parts = []
        
        # Type and name
        parts.append(f"{fragment.type}: {fragment.name}")
        
        # Signature
        parts.append(f"Signature: {fragment.signature}")
        
        # Platform and action
        platform = fragment.metadata.get('platform', 'unknown')
        action = fragment.metadata.get('action', 'unknown')
        parts.append(f"Platform: {platform}, Action: {action}")
        
        # Docstring
        if fragment.docstring:
            parts.append(f"Description: {fragment.docstring}")
        
        # Source code (first 500 chars for context)
        code_preview = fragment.source_code[:500]
        parts.append(f"Code:\n{code_preview}")
        
        return "\n".join(parts)
    
    def search(self,
               query: str,
               n_results: int = 5,
               platform: Optional[str] = None,
               action: Optional[str] = None,
               code_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant code fragments
        
        Args:
            query: Natural language query (e.g., "login to instagram")
            n_results: Number of results to return
            platform: Filter by platform (instagram, tiktok, etc.)
            action: Filter by action (login, like, follow, etc.)
            code_type: Filter by type (function, class, method)
        
        Returns:
            List of relevant code fragments with metadata
        """
        logger.info(f"🔍 Searching for: '{query}'")
        
        # Build metadata filter
        where_filter = {}
        if platform:
            where_filter['platform'] = platform
        if action:
            where_filter['action'] = action
        if code_type:
            where_filter['type'] = code_type
        
        # Perform search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else None
        )
        
        # Format results
        formatted_results = []
        
        if results['ids'][0]:  # Check if we have results
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'metadata': results['metadatas'][0][i],
                    'source_code': results['metadatas'][0][i].get('source_code', ''),
                    'relevance_score': 1 - (results['distances'][0][i] if 'distances' in results else 0)
                }
                formatted_results.append(result)
        
        logger.info(f"✅ Found {len(formatted_results)} relevant fragments")
        
        return formatted_results
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get code fragment by exact name"""
        results = self.collection.get(
            where={"name": name}
        )
        
        if results['ids']:
            return {
                'id': results['ids'][0],
                'metadata': results['metadatas'][0],
                'source_code': results['metadatas'][0].get('source_code', '')
            }
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the code vault"""
        count = self.collection.count()
        
        if count == 0:
            return {"total_fragments": 0}
        
        # Get all metadata to compute stats
        all_data = self.collection.get()
        
        stats = {
            "total_fragments": count,
            "by_platform": {},
            "by_action": {},
            "by_type": {}
        }
        
        for metadata in all_data['metadatas']:
            platform = metadata.get('platform', 'unknown')
            action = metadata.get('action', 'unknown')
            code_type = metadata.get('type', 'unknown')
            
            stats['by_platform'][platform] = stats['by_platform'].get(platform, 0) + 1
            stats['by_action'][action] = stats['by_action'].get(action, 0) + 1
            stats['by_type'][code_type] = stats['by_type'].get(code_type, 0) + 1
        
        return stats
    
    def clear(self) -> None:
        """Clear all fragments from the vault (use with caution!)"""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(self.collection.name)
        logger.warning("⚠️ Code Vault cleared!")


# Example usage and CLI
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    import sys
    
    # Initialize vault
    vault = CodeVault()
    
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        # Ingest mode
        legacy_path = sys.argv[2] if len(sys.argv) > 2 else "./legacy_code"
        
        logger.info(f"🚀 Ingesting code from: {legacy_path}")
        
        # Parse legacy code
        ingestor = CodeIngestor(legacy_path)
        fragments = ingestor.scan_and_parse()
        
        # Ingest into vault
        vault.ingest_fragments(fragments)
        
        # Show stats
        stats = vault.get_stats()
        print(f"\n📊 Code Vault Statistics:")
        print(json.dumps(stats, indent=2))
    
    elif len(sys.argv) > 1 and sys.argv[1] == "search":
        # Search mode
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "login to instagram"
        
        logger.info(f"🔍 Searching for: '{query}'")
        
        results = vault.search(query, n_results=3)
        
        print(f"\n🎯 Search Results ({len(results)}):")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['metadata']['name']} ({result['metadata']['type']})")
            print(f"   Platform: {result['metadata']['platform']}, Action: {result['metadata']['action']}")
            print(f"   Relevance: {result['relevance_score']:.2%}")
            print(f"   Signature: {result['metadata']['signature']}")
            print(f"   Code preview:")
            print(f"   {result['source_code'][:200]}...")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "stats":
        # Stats mode
        stats = vault.get_stats()
        print(f"\n📊 Code Vault Statistics:")
        print(json.dumps(stats, indent=2))
    
    else:
        print("Usage:")
        print("  python code_vault.py ingest [path]    - Ingest legacy code")
        print("  python code_vault.py search [query]   - Search code fragments")
        print("  python code_vault.py stats            - Show vault statistics")
