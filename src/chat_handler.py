"""
Chat Handler Module
Handles query processing, response formatting, and query logging
"""

import os
from datetime import datetime
from typing import Dict, Any
from .gemini_client import GeminiClient


class ChatHandler:
    """Handles chat/query operations and logging"""

    def __init__(self, gemini_client: GeminiClient, document_manager, log_path: str = "data/query_history.txt"):
        """
        Initialize Chat Handler

        Args:
            gemini_client: Instance of GeminiClient
            document_manager: Document manager instance for getting file list
            log_path: Path to query history log file
        """
        self.client = gemini_client
        self.document_manager = document_manager
        self.log_path = log_path
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Ensure the log file and directory exist"""
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            if not os.path.exists(self.log_path):
                with open(self.log_path, 'w', encoding='utf-8') as f:
                    f.write("# FileRAG Query History\n")
                    f.write(f"# Created: {datetime.now().isoformat()}\n")
                    f.write("=" * 80 + "\n\n")
        except Exception as e:
            print(f"Warning: Could not create log file: {str(e)}")

    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a query using uploaded files as context

        Args:
            question: User's question

        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            # Get all document file names
            file_names = self.document_manager.get_all_document_names()

            if not file_names:
                return {
                    'question': question,
                    'answer': "No documents available to query. Please upload documents first.",
                    'sources': [],
                    'found': False,
                    'timestamp': datetime.now().isoformat()
                }

            # Query using files as context
            result = self.client.query_with_files(
                query=question,
                file_names=file_names
            )

            # Format response
            response = {
                'question': question,
                'answer': result['answer'],
                'sources': result['sources'],
                'found': result['found'],
                'timestamp': datetime.now().isoformat()
            }

            # Log the query and response
            self._log_query(response)

            return response

        except Exception as e:
            error_response = {
                'question': question,
                'answer': f"Error processing query: {str(e)}",
                'sources': [],
                'found': False,
                'timestamp': datetime.now().isoformat()
            }

            # Log the error
            self._log_query(error_response)

            return error_response

    def _log_query(self, response: Dict[str, Any]) -> None:
        """
        Log query and response to file

        Args:
            response: Query response dictionary
        """
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"Timestamp: {response['timestamp']}\n")
                f.write(f"Query: {response['question']}\n")
                f.write(f"\nAnswer: {response['answer']}\n")

                if response['sources']:
                    f.write(f"\nSources:\n")
                    for idx, source in enumerate(response['sources'], 1):
                        f.write(f"  {idx}. Document: {source.get('document', 'Unknown')}\n")
                        if source.get('chunk'):
                            f.write(f"     Chunk: {source['chunk'][:100]}...\n")
                else:
                    f.write(f"\nSources: No sources found\n")

                f.write(f"Status: {'Found' if response['found'] else 'Not Found'}\n")
                f.write(f"{'=' * 80}\n\n")

        except Exception as e:
            print(f"Warning: Failed to log query: {str(e)}")

    def format_response_for_display(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format response for display in UI

        Args:
            response: Query response dictionary

        Returns:
            Formatted response for UI display
        """
        # Always show the actual answer from Gemini
        answer = response.get('answer', 'No response generated')

        # Format sources for display
        formatted_sources = []
        if response.get('sources'):
            for idx, source in enumerate(response['sources'], 1):
                formatted_sources.append({
                    'index': idx,
                    'document': source.get('document', 'Unknown'),
                    'chunk': source.get('chunk', '')
                })

        # Return the response with the actual answer
        return {
            'message': answer,
            'answer': answer,
            'sources': formatted_sources,
            'has_answer': bool(answer and answer != 'No response generated')
        }

    def get_query_history(self) -> str:
        """
        Get the full query history

        Returns:
            Query history as string
        """
        try:
            if os.path.exists(self.log_path):
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return "No query history available"
        except Exception as e:
            return f"Error reading query history: {str(e)}"

    def clear_history(self) -> bool:
        """
        Clear the query history

        Returns:
            True if successful
        """
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                f.write("# FileRAG Query History\n")
                f.write(f"# Cleared: {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
            return True
        except Exception as e:
            print(f"Error clearing history: {str(e)}")
            return False

    def get_query_count(self) -> int:
        """
        Get the total number of queries logged

        Returns:
            Number of queries
        """
        try:
            if not os.path.exists(self.log_path):
                return 0

            with open(self.log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Count occurrences of "Query:" which indicates a logged query
                return content.count("Query:")
        except:
            return 0

    def save_rating(self, question: str, answer: str, rating: int, note: str = None) -> bool:
        """
        Save rating for a query/answer pair to the log file

        Args:
            question: The user's question
            answer: The assistant's answer
            rating: Rating from 1-5
            note: Optional note/feedback

        Returns:
            True if successful
        """
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'*' * 80}\n")
                f.write(f"RATING SUBMITTED: {datetime.now().isoformat()}\n")
                f.write(f"Question: {question}\n")
                f.write(f"Rating: {'⭐' * rating} ({rating}/5)\n")
                if note:
                    f.write(f"Note: {note}\n")
                f.write(f"{'*' * 80}\n\n")
            return True
        except Exception as e:
            print(f"Error saving rating: {str(e)}")
            return False
