from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

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

    def create_project(self, project_id, thread_id):
        logger.info(f"Creating new project with ID: {project_id}")
        project = {
            'project_id': project_id,
            'thread_id': thread_id,
            'documents': [],  # Will store document metadata and S3 keys
            'state': {
                'project_id': project_id,
                'current_phase': 0,
                'current_language': 'en',
                'slides': {},
                'html_preview': False,
                'pdf_generated': False,
                'timestamp': datetime.now().isoformat(),
            },
            'created_at': datetime.now()
        }
        
        result = self.projects.update_one(
            {'project_id': project_id},
            {'$set': project},
            upsert=True
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated existing project: {project_id}")
        elif result.upserted_id:
            logger.info(f"Created new project: {project_id}")
        
        return project

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

    def get_project(self, project_id):
        logger.info(f"Retrieving project: {project_id}")
        project = self.projects.find_one({'project_id': project_id})
        if project:
            logger.info(f"Found project: {project_id}")
        else:
            logger.warning(f"Project not found: {project_id}")
        return project

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

    def update_project_language(self, project_id, language):
        logger.info(f"Updating language for project {project_id} to: {language}")
        result = self.projects.update_one(
            {'project_id': project_id},
            {'$set': {'state.current_language': language}}
        )
        if result.modified_count > 0:
            logger.info(f"Successfully updated language for project: {project_id}")
        else:
            logger.warning(f"Failed to update language for project: {project_id}")
        return result.modified_count > 0

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

    def delete_project(self, project_id):
        logger.info(f"Deleting project: {project_id}")
        result = self.projects.delete_one({'project_id': project_id})
        if result.deleted_count > 0:
            logger.info(f"Successfully deleted project: {project_id}")
        else:
            logger.warning(f"Failed to delete project: {project_id}")
        return result.deleted_count > 0 