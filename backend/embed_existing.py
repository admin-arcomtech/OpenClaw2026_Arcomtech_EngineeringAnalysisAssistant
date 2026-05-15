"""
Batch embed all cases with NULL embedding. Run after Sprint 3 deploy
or after seed_cases.py to bootstrap pgvector similarity search.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.services.embedding_service import embed_all_pending

if __name__ == "__main__":
    n = embed_all_pending(limit=1000)
    print(f"Embedded {n} case(s).")
