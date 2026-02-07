import os
import json
import logging
from typing import List, Dict, Optional, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Configure logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleTasksManager:
    """Manager for Google Tasks operations using stored OAuth tokens."""
    
    def __init__(self, token_path: str = "config/google_token.json"):
        self.token_path = token_path
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Load credentials from token file."""
        try:
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(self.token_path)
                
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Token expired, refreshing...")
                    self.creds.refresh(Request())
                    # Save refreshed token
                    with open(self.token_path, 'w') as token:
                        token.write(self.creds.to_json())
                else:
                    logger.warning(f"No valid token found at {self.token_path}. Authentication required.")
                    return

            self.service = build('tasks', 'v1', credentials=self.creds)
            logger.info("Google Tasks Service initialized successfully.")
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Tasks: {e}")

    def list_task_lists(self) -> List[Dict[str, Any]]:
        """List all task lists."""
        if not self.service:
            logger.warning("Service not initialized.")
            return []
            
        try:
            results = self.service.tasklists().list(maxResults=10).execute()
            items = results.get('items', [])
            return items
        except Exception as e:
            logger.error(f"Error listing task lists: {e}")
            return []

    def get_default_task_list_id(self) -> Optional[str]:
        """Get the ID of the default task list (usually the first one or named 'My Tasks')."""
        lists = self.list_task_lists()
        if lists:
            return lists[0]['id']
        return None

    def create_task(self, title: str, task_list_id: Optional[str] = None, notes: Optional[str] = None, due: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new task. If task_list_id is None, uses default."""
        if not self.service:
            logger.warning("Service not initialized, cannot create task.")
            return None
            
        try:
            if not task_list_id:
                task_list_id = self.get_default_task_list_id()
                if not task_list_id:
                    logger.error("No task list found.")
                    return None

            body = {'title': title}
            if notes:
                body['notes'] = notes
            if due:
                body['due'] = due # RFC 3339 timestamp
                
            result = self.service.tasks().insert(tasklist=task_list_id, body=body).execute()
            logger.info(f"Task created: {result.get('title')}")
            return result
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    def list_tasks(self, task_list_id: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """List tasks from a task list."""
        if not self.service:
            return []
            
        try:
            if not task_list_id:
                task_list_id = self.get_default_task_list_id()
                if not task_list_id:
                    return []

            results = self.service.tasks().list(tasklist=task_list_id, maxResults=max_results, showCompleted=False).execute()
            items = results.get('items', [])
            return items
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return []
