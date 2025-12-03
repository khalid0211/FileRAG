"""
FileRAG - File-based Retrieval Augmented Generation using Google Gemini
"""

from .gemini_client import GeminiClient
from .store_manager import StoreManager
from .document_manager import DocumentManager
from .chat_handler import ChatHandler

__all__ = ['GeminiClient', 'StoreManager', 'DocumentManager', 'ChatHandler']
