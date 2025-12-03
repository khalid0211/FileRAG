"""
Store Manager Module
Handles store initialization and configuration persistence
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from .gemini_client import GeminiClient


class StoreManager:
    """Manages document store lifecycle and configuration"""

    def __init__(self, gemini_client: GeminiClient, config_path: str = "data/config.json"):
        """
        Initialize Store Manager

        Args:
            gemini_client: Instance of GeminiClient
            config_path: Path to configuration file
        """
        self.client = gemini_client
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file

        Returns:
            Configuration dictionary
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'store_initialized': False,
                    'store_name': None,
                    'created_at': None
                }
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return {
                'store_initialized': False,
                'store_name': None,
                'created_at': None
            }

    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save config: {str(e)}")

    def store_exists(self) -> bool:
        """
        Check if a store is already initialized

        Returns:
            True if store exists and is initialized
        """
        return self.config.get('store_initialized', False)

    def create_store(self, store_name: str = "filerag_store") -> Dict[str, Any]:
        """
        Initialize a new document store

        Args:
            store_name: Name for the store

        Returns:
            Dictionary with store details
        """
        try:
            # Check if store already exists
            if self.store_exists():
                return {
                    'success': False,
                    'message': 'Store already exists',
                    'store_name': self.config['store_name']
                }

            # Save configuration
            self.config['store_initialized'] = True
            self.config['store_name'] = store_name
            self.config['created_at'] = datetime.now().isoformat()
            self._save_config()

            return {
                'success': True,
                'message': 'Store initialized successfully',
                'store_name': store_name,
                'created_at': self.config['created_at']
            }

        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to initialize store: {str(e)}",
                'store_name': None
            }

    def get_store_info(self) -> Dict[str, Any]:
        """
        Get information about the current store

        Returns:
            Dictionary with store information
        """
        if not self.store_exists():
            return {
                'exists': False,
                'message': 'No store configured'
            }

        try:
            # Get file count from Gemini
            files = self.client.list_files()

            return {
                'exists': True,
                'store_name': self.config.get('store_name', 'Unknown'),
                'created_at': self.config.get('created_at', 'Unknown'),
                'document_count': len(files) if files else 0
            }
        except Exception as e:
            return {
                'exists': True,
                'store_name': self.config.get('store_name', 'Unknown'),
                'created_at': self.config.get('created_at', 'Unknown'),
                'document_count': 0,
                'error': str(e)
            }

    def delete_store(self) -> Dict[str, Any]:
        """
        Delete all files and reset configuration

        Returns:
            Dictionary with deletion status
        """
        try:
            if not self.config.get('store_initialized'):
                return {
                    'success': False,
                    'message': 'No store to delete'
                }

            # Delete all uploaded files
            try:
                files = self.client.list_files()
                for file in files:
                    try:
                        self.client.delete_file(file.name)
                    except:
                        pass  # Continue even if some files fail to delete
            except:
                pass

            # Reset configuration
            self.config = {
                'store_initialized': False,
                'store_name': None,
                'created_at': None
            }
            self._save_config()

            return {
                'success': True,
                'message': 'Store deleted successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to delete store: {str(e)}"
            }

    def get_store_name(self) -> Optional[str]:
        """
        Get the current store name

        Returns:
            Store name or None if not configured
        """
        return self.config.get('store_name')
