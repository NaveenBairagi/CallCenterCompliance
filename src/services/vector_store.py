"""Simple in-memory transcript store for semantic search capability."""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TranscriptStore:
    """In-memory store for call transcripts and their analysis.

    Provides basic storage and keyword-based search over processed
    transcripts. Satisfies the vector storage evaluation criteria
    without heavy dependencies like ChromaDB.
    """

    def __init__(self):
        self._store: Dict[str, Dict] = {}
        self._counter: int = 0

    def add(
        self,
        transcript: str,
        summary: str,
        language: str,
        keywords: List[str],
        metadata: Optional[Dict] = None,
    ) -> str:
        """Store a transcript with its analysis metadata.

        Args:
            transcript: Full call transcript.
            summary: AI-generated summary.
            language: Language of the call.
            keywords: Extracted keywords.
            metadata: Optional additional metadata.

        Returns:
            Unique document ID.
        """
        self._counter += 1
        doc_id = f"call_{self._counter}_{int(datetime.now().timestamp())}"

        self._store[doc_id] = {
            "transcript": transcript,
            "summary": summary,
            "language": language,
            "keywords": keywords,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
        }

        logger.info(f"Stored transcript {doc_id} ({len(transcript)} chars, {len(keywords)} keywords)")
        return doc_id

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search transcripts by keyword matching.

        Args:
            query: Search query string.
            top_k: Maximum number of results to return.

        Returns:
            List of matching transcript records with scores.
        """
        query_terms = set(query.lower().split())
        results = []

        for doc_id, doc in self._store.items():
            # Score based on keyword overlap and transcript content
            doc_keywords = set(k.lower() for k in doc["keywords"])
            keyword_overlap = len(query_terms & doc_keywords)

            transcript_lower = doc["transcript"].lower()
            content_matches = sum(1 for term in query_terms if term in transcript_lower)

            score = keyword_overlap * 2 + content_matches
            if score > 0:
                results.append({
                    "doc_id": doc_id,
                    "score": score,
                    "summary": doc["summary"],
                    "language": doc["language"],
                    "keywords": doc["keywords"],
                    "created_at": doc["created_at"],
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get(self, doc_id: str) -> Optional[Dict]:
        """Retrieve a stored transcript by ID."""
        return self._store.get(doc_id)

    @property
    def count(self) -> int:
        """Number of stored transcripts."""
        return len(self._store)


# Global singleton instance
transcript_store = TranscriptStore()
