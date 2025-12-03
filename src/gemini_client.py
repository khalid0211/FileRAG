"""
Gemini API Client Module
Handles all interactions with Google's Gemini API for file upload and querying
"""

import google.generativeai as genai
from typing import Optional, List, Dict, Any
import time


class GeminiClient:
    """Client for interacting with Gemini File API"""

    def __init__(self, api_key: str):
        """
        Initialize Gemini client with API key

        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.api_key = api_key
        # Use Gemini 2.5 Flash - stable model with file support
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')

    def upload_file(self, file_path: str, display_name: Optional[str] = None, mime_type: Optional[str] = None) -> Any:
        """
        Upload a file to Gemini

        Args:
            file_path: Path to the file to upload
            display_name: Optional display name for the file
            mime_type: MIME type of the file

        Returns:
            Uploaded file object
        """
        try:
            file = genai.upload_file(
                path=file_path,
                display_name=display_name,
                mime_type=mime_type
            )

            # Wait for file to be processed
            while file.state.name == "PROCESSING":
                time.sleep(1)
                file = genai.get_file(file.name)

            if file.state.name == "FAILED":
                raise Exception(f"File processing failed: {file.name}")

            return file
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def list_files(self) -> List[Any]:
        """
        List all uploaded files

        Returns:
            List of file objects
        """
        try:
            files = list(genai.list_files())
            return files
        except Exception as e:
            raise Exception(f"Failed to list files: {str(e)}")

    def get_file(self, file_name: str) -> Optional[Any]:
        """
        Get a file by name

        Args:
            file_name: Name of the file

        Returns:
            File object if found
        """
        try:
            file = genai.get_file(file_name)
            return file
        except Exception as e:
            print(f"File not found: {str(e)}")
            return None

    def delete_file(self, file_name: str) -> bool:
        """
        Delete an uploaded file

        Args:
            file_name: Name of the file to delete

        Returns:
            True if successful
        """
        try:
            genai.delete_file(file_name)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete file: {str(e)}")

    def query_with_files(self, query: str, file_names: List[str]) -> Dict[str, Any]:
        """
        Query using uploaded files as context

        Args:
            query: User's question/query
            file_names: List of file names to use as context

        Returns:
            Dictionary with answer and sources
        """
        try:
            # Get file objects
            files = []
            failed_files = []

            for file_name in file_names:
                try:
                    file = genai.get_file(file_name)

                    # Check if file is ready
                    if hasattr(file, 'state') and file.state.name == "ACTIVE":
                        files.append(file)
                    elif hasattr(file, 'state'):
                        failed_files.append(f"{file_name} (state: {file.state.name})")
                    else:
                        files.append(file)  # Add anyway if no state attribute

                except Exception as e:
                    failed_files.append(f"{file_name} (error: {str(e)})")
                    continue

            if not files:
                error_msg = "No active documents available to query."
                if failed_files:
                    error_msg += f"\n\nFailed files: {', '.join(failed_files)}"
                return {
                    'answer': error_msg,
                    'sources': [],
                    'found': False,
                    'debug_info': {
                        'total_file_names': len(file_names),
                        'active_files': 0,
                        'failed_files': failed_files
                    }
                }

            # Create prompt with context
            context_prompt = f"""You are a helpful assistant that answers questions based on provided documents.

Read the following documents carefully and answer the user's question based ONLY on the information in these documents.

If the answer is found in the documents, provide a detailed answer and cite which document(s) it came from.
If the answer is NOT found in the documents, respond with: "I don't have this information in the provided documents."

Question: {query}"""

            # Generate content with files as context
            print(f"DEBUG: Querying with {len(files)} files: {[f.name for f in files]}")
            response = self.model.generate_content([context_prompt] + files)

            # Extract answer
            answer = response.text if response.text else "No answer generated"
            print(f"DEBUG: Got response: {answer[:200]}...")

            # Extract file sources
            sources = []
            for file in files:
                sources.append({
                    'document': file.display_name if hasattr(file, 'display_name') else file.name,
                    'file_name': file.name
                })

            # Check if information was found
            # Assume found=True UNLESS Gemini explicitly says it doesn't have the info
            not_found_phrases = [
                "i don't have this information",
                "i don't have",
                "not found in the",
                "not available in the",
                "cannot find this",
                "no information about",
                "don't see any information"
            ]

            found = True
            answer_lower = answer.lower()
            for phrase in not_found_phrases:
                if phrase in answer_lower:
                    found = False
                    break

            # If we have sources and an answer, it's probably found
            if sources and len(answer) > 50:  # Meaningful answer length
                found = True

            return {
                'answer': answer,
                'sources': sources,
                'found': found,
                'debug_info': {
                    'total_file_names': len(file_names),
                    'active_files': len(files),
                    'failed_files': failed_files
                }
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR in query_with_files: {error_details}")
            return {
                'answer': f"Error processing query: {str(e)}\n\nPlease check the console for details.",
                'sources': [],
                'found': False,
                'debug_info': {
                    'error': str(e),
                    'error_details': error_details
                }
            }
