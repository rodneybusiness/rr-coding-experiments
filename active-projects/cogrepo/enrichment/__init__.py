"""
AI enrichment pipeline for conversation processing.

Uses Claude API to generate:
- Meaningful titles
- Abstractive and extractive summaries
- Tags and topics
- Quality scores and insights
"""

from .enrichment_pipeline import EnrichmentPipeline

__all__ = ["EnrichmentPipeline"]
