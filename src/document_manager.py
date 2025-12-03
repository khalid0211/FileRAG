"""
Document Manager Module
Handles document upload, listing, and deletion operations
"""

import os
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime
from .gemini_client import GeminiClient


class DocumentManager:
    """Manages document operations"""

    def __init__(self, gemini_client: GeminiClient, store_name: str = None):
        """
        Initialize Document Manager

        Args:
            gemini_client: Instance of GeminiClient
            store_name: Name of the store (for reference only)
        """
        self.client = gemini_client
        self.store_name = store_name

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all uploaded documents

        Returns:
            List of dictionaries containing document information
        """
        try:
            files = self.client.list_files()

            doc_list = []
            for file in files:
                doc_info = {
                    'name': file.name,
                    'display_name': file.display_name if hasattr(file, 'display_name') else os.path.basename(file.name),
                    'create_time': str(file.create_time) if hasattr(file, 'create_time') else 'Unknown',
                    'update_time': str(file.update_time) if hasattr(file, 'update_time') else 'Unknown',
                    'uri': file.uri if hasattr(file, 'uri') else None
                }
                doc_list.append(doc_info)

            return doc_list

        except Exception as e:
            raise Exception(f"Failed to list documents: {str(e)}")

    def upload_document(self, uploaded_file, display_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a document

        Args:
            uploaded_file: Streamlit UploadedFile object or file path
            display_name: Optional display name for the document

        Returns:
            Dictionary with upload status and document info
        """
        try:
            # Determine the file display name first
            if hasattr(uploaded_file, 'read'):
                file_display_name = display_name or uploaded_file.name
            else:
                file_display_name = display_name or os.path.basename(uploaded_file)

            # Check for duplicates before uploading
            try:
                existing_docs = self.list_documents()
                for doc in existing_docs:
                    if doc['display_name'] == file_display_name:
                        return {
                            'success': False,
                            'message': f'Document "{file_display_name}" already exists. Please delete it first or rename the file.',
                            'document_name': None,
                            'duplicate': True
                        }
            except Exception as e:
                # If we can't check for duplicates, log a warning but continue
                print(f"Warning: Could not check for duplicates: {str(e)}")

            # Handle Streamlit UploadedFile object
            if hasattr(uploaded_file, 'read'):
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name

                mime_type = uploaded_file.type if hasattr(uploaded_file, 'type') else None

            else:
                # Handle file path
                tmp_path = uploaded_file
                mime_type = None

            try:
                # Upload file to Gemini
                file_object = self.client.upload_file(
                    file_path=tmp_path,
                    display_name=file_display_name,
                    mime_type=mime_type
                )

                return {
                    'success': True,
                    'message': f'Document "{file_display_name}" uploaded successfully',
                    'document_name': file_object.name,
                    'display_name': file_display_name
                }

            finally:
                # Clean up temporary file if it was created
                if hasattr(uploaded_file, 'read') and os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to upload document: {str(e)}",
                'document_name': None
            }

    def delete_document(self, document_name: str) -> Dict[str, Any]:
        """
        Delete a document

        Args:
            document_name: Full name of the document to delete

        Returns:
            Dictionary with deletion status
        """
        try:
            self.client.delete_file(document_name)

            return {
                'success': True,
                'message': f'Document deleted successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to delete document: {str(e)}"
            }

    def get_document_count(self) -> int:
        """
        Get the total number of documents

        Returns:
            Number of documents
        """
        try:
            documents = self.list_documents()
            return len(documents)
        except:
            return 0

    def get_all_document_names(self) -> List[str]:
        """
        Get list of all document file names

        Returns:
            List of file names
        """
        try:
            documents = self.list_documents()
            return [doc['name'] for doc in documents]
        except:
            return []

    def batch_upload_documents(self, uploaded_files: List) -> Dict[str, Any]:
        """
        Upload multiple documents

        Args:
            uploaded_files: List of Streamlit UploadedFile objects or file paths

        Returns:
            Dictionary with batch upload results
        """
        results = {
            'total': len(uploaded_files),
            'successful': 0,
            'failed': 0,
            'details': []
        }

        for file in uploaded_files:
            result = self.upload_document(file)
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1

            results['details'].append({
                'file': file.name if hasattr(file, 'name') else os.path.basename(file),
                'success': result['success'],
                'message': result['message']
            })

        return results
