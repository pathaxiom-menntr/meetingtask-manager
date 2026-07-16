"""
app/services/ai/__init__.py

Public surface of the ai package.

Re-exports AIService so that existing callers need NO import changes:
    from app.services.ai import AIService   # still works
"""

from .pipeline import AIService

__all__ = ["AIService"]
