from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DatabaseManager')

load_dotenv()

class DatabaseManager:
    def __init__(self):
        mongo_uri = os.getenv('MONGODB_URI')
        if not mongo_uri:
            logger.error("MongoDB URI not found in environment variables")
            raise ValueError("MongoDB URI not found in environment variables")
        
        logger.info("Initializing DatabaseManager")
        self.client = MongoClient(mongo_uri)
        self.db = self.client.pitchdeck
        self.projects = self.db.projects
        logger.info("Successfully connected to MongoDB")
        
        # Run migration
        self.migrate_add_deleted_flag()

    def migrate_add_deleted_flag(self):
        """One-time migration to add deleted flag to existing projects"""
        try:
            self.projects.update_many(
                {'deleted': {'$exists': False}},
                {'$set': {'deleted': False}}
            )
            logger.info("Successfully added deleted flag to existing projects")
        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")

    def create_project(self, project_id: str, thread_id: str, token: str) -> dict:
        """Create a new project with token"""
        project = {
            'project_id': project_id,
            'thread_id': thread_id,
            'token': token,
            'created_at': datetime.now(),
            'state': {
                'current_language': 'en',
                'slides': {}
            },
            'documents': [],
            'deleted': False  # Add deleted flag
        }
        try:
            # First check if a deleted project exists
            existing = self.projects.find_one({'project_id': project_id})
            if existing:
                # If it exists but is marked as deleted, update it
                self.projects.update_one(
                    {'project_id': project_id},
                    {
                        '$set': project
                    }
                )
            else:
                # Otherwise create new
                self.projects.insert_one(project)
            
            logger.info(f"Created new project: {project_id}")
            return project
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise

    def add_document(self, project_id, document_metadata):
        """Add document metadata with S3 reference"""
        logger.info(f"Adding document metadata for project {project_id}: {document_metadata['filename']}")
        result = self.projects.update_one(
            {'project_id': project_id},
            {'$push': {'documents': document_metadata}}
        )
        if result.modified_count > 0:
            logger.info(f"Successfully added document metadata to project: {project_id}")
        else:
            logger.warning(f"Failed to add document metadata to project: {project_id}")
        return result.modified_count > 0

    def get_project_documents(self, project_id):
        """Get all document metadata for a project"""
        logger.info(f"Retrieving documents for project: {project_id}")
        project = self.projects.find_one(
            {'project_id': project_id},
            {'documents': 1}
        )
        documents = project.get('documents', []) if project else []
        logger.info(f"Found {len(documents)} documents for project: {project_id}")
        return documents

    def get_project(self, project_id: str) -> Optional[dict]:
        """Get project with default state structure"""
        logger.info(f"Retrieving project: {project_id}")
        try:
            # Use find_one with explicit query and projection
            project = self.projects.find_one(
                {
                    'project_id': project_id,
                    'deleted': {'$ne': True}  # Only get non-deleted projects
                },
                {
                    '_id': 0,
                    'project_id': 1,
                    'thread_id': 1,
                    'token': 1,
                    'state': 1,
                    'documents': 1,
                    'deleted': 1
                }
            )
            
            if project:
                logger.info(f"Found project: {project_id}")
                if 'state' not in project:
                    project['state'] = {
                        'current_language': 'en',
                        'slides': {}
                    }
                    self.projects.update_one(
                        {'project_id': project_id},
                        {'$set': {'state': project['state']}}
                    )
            else:
                logger.info(f"No active project found with ID: {project_id}")
            
            return project
            
        except Exception as e:
            logger.error(f"Error retrieving project: {str(e)}")
            return None

    def update_project_documents(self, project_id, documents):
        logger.info(f"Updating documents for project {project_id} with {len(documents)} documents")
        result = self.projects.update_one(
            {'project_id': project_id},
            {'$push': {'documents': {'$each': documents}}}
        )
        if result.modified_count > 0:
            logger.info(f"Successfully updated documents for project: {project_id}")
        else:
            logger.warning(f"Failed to update documents for project: {project_id}")
        return result.modified_count > 0

    def update_project_language(self, project_id: str, language: str) -> bool:
        """Update project language and return the updated project"""
        logger.info(f"Updating language for project {project_id} to: {language}")
        try:
            result = self.projects.update_one(
                {'project_id': project_id},
                {
                    '$set': {
                        'state.current_language': language,
                    }
                }
            )
            if result.modified_count > 0:
                logger.info(f"Successfully updated language for project: {project_id}")
                return True
            else:
                logger.warning(f"Failed to update language for project: {project_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating language: {str(e)}")
            return False

    def update_slide_content(self, project_id, slide_type, content):
        logger.info(f"Updating slide content for project {project_id}, slide: {slide_type}")
        result = self.projects.update_one(
            {'project_id': project_id},
            {'$set': {f'state.slides.{slide_type}': content}}
        )
        if result.modified_count > 0:
            logger.info(f"Successfully updated slide content for project: {project_id}")
        else:
            logger.warning(f"Failed to update slide content for project: {project_id}")
        return result.modified_count > 0

    def delete_project(self, project_id: str) -> bool:
        """Delete project and all associated data"""
        logger.info(f"Starting deletion process for project: {project_id}")
        try:
            # First, get the project to verify it exists
            project = self.get_project(project_id)
            if not project:
                logger.warning(f"Project not found for deletion: {project_id}")
                return False

            # Mark the project as deleted first
            result = self.projects.update_one(
                {'project_id': project_id},
                {
                    '$set': {
                        'deleted': True,
                        'deleted_at': datetime.now()
                    }
                }
            )

            if result.modified_count > 0:
                logger.info(f"Successfully marked project as deleted: {project_id}")
                
                # Clear any cached data
                if hasattr(self, '_document_cache'):
                    self._document_cache.pop(project_id, None)
                if hasattr(self, '_slide_cache'):
                    self._slide_cache.pop(project_id, None)
                if hasattr(self, '_html_cache'):
                    self._html_cache.pop(project_id, None)
                
                return True
            else:
                logger.error(f"Failed to mark project as deleted: {project_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            logger.error(f"Full error details: {e.__class__.__name__}: {str(e)}")
            return False

    def get_project_by_token(self, token: str) -> Optional[dict]:
        """Retrieve project by token"""
        return self.projects.find_one({
            'token': token,
            'deleted': {'$ne': True}  # Only get non-deleted projects
        })

    def get_slide_content(self, project_id: str, slide_type: str) -> Optional[str]:
        """Retrieve content for a specific slide"""
        project = self.projects.find_one(
            {'project_id': project_id},
            {f'state.slides.{slide_type}': 1}
        )
        
        if project and 'state' in project and 'slides' in project['state']:
            return project['state']['slides'].get(slide_type)
        return None 

    def update_project_token(self, project_id: str, token: str) -> bool:
        """Update or add token to existing project"""
        logger.info(f"Updating token for project: {project_id}")
        try:
            # Update project with token and ensure state structure exists
            result = self.projects.update_one(
                {'project_id': project_id},
                {
                    '$set': {
                        'token': token,
                        'state': {
                            'current_language': 'en',
                            'slides': {}
                        }
                    }
                },
                upsert=False
            )
            
            if result.modified_count > 0:
                logger.info(f"Successfully updated token for project: {project_id}")
                return True
            else:
                logger.warning(f"Failed to update token for project: {project_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error updating project token: {str(e)}")
            return False 