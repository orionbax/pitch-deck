import streamlit as st
import time
import json
from datetime import datetime
from typing import Optional, Dict
from vector_store import VectorStore

class ProjectState:
    def __init__(self, project_id: str, vector_store: VectorStore, user, client):
        self.project_id = project_id
        self.vector_store = vector_store
        self.current_phase = 0
        self.current_language = "no"
        self.slides = {}
        self.phase_reports = {}
        self.feedback_history = {}
        self.html_preview = None
        self.pdf_generated = False
        self.user = user # -> session['user_id']
        self.client = client
    
    def save_state(self) -> bool:
        """Store current state in vector store with improved error handling"""
        try:
            state_data = {
                'project_id': self.project_id,
                'current_phase': self.current_phase,
                'current_language': self.current_language,
                'slides': self.slides,
                'phase_reports': self.phase_reports,
                'feedback_history': self.feedback_history,
                'html_preview': self.html_preview,
                'pdf_generated': self.pdf_generated,
                'timestamp': datetime.now().isoformat()
            }

            # Convert state data to JSON string
            state_json = json.dumps(state_data)

            # Store in vector store
            success = self.vector_store.store_state(self.project_id, state_json)

            if not success:
                print("Failed to store project state in vector store")
                return False

            self.user['last_saved_state'] = state_data
            return True

        except Exception as e:
            print(f"Error saving state: {str(e)}")
            return False
    
    def delete_state(self) -> bool:
        """Delete current state from vector store and Pinecone"""
        try:
            # Delete from vector store
            success = self.vector_store.delete_project_state(self.project_id)
            
            if not success:
                print("Failed to delete project state from vector store")
                return False

            # Delete from Pinecone
            namespace = self.vector_store.get_project_namespace(self.project_id, 'state')
            try:
                self.vector_store.index.delete(
                    namespace=namespace,
                    delete_all=True
                )
            except Exception as e:
                print(f"Failed to delete state from Pinecone: {str(e)}")
                return False

            # Reset instance variables
            self.current_phase = 0
            self.current_language = "no" 
            self.slides = {}
            self.phase_reports = {}
            self.feedback_history = {}
            self.html_preview = None
            self.pdf_generated = False

            # Clear saved state from user session
            if 'last_saved_state' in self.user:
                del self.user['last_saved_state']

            return True

        except Exception as e:
            print(f"Error deleting state: {str(e)}")
            return False
  
    def load_state(self) -> bool:
        """Load state from vector store"""
        try:
            state_data = self.vector_store.get_project_state(self.project_id) or {}

            if not state_data:
                self.current_phase = state_data.get('current_phase', 0)
                self.current_language = state_data.get('current_language', 'en')
                self.slides = state_data.get('slides', {})
                self.phase_reports = state_data.get('phase_reports', {})
                self.feedback_history = state_data.get('feedback_history', {})
                self.html_preview = state_data.get('html_preview')
                self.pdf_generated = state_data.get('pdf_generated', False)
                self.user['last_saved_state'] = state_data
                # return True
            self.user['last_saved_state'] = {
                'current_phase': self.current_phase,
                'current_language': self.current_language,
                'slides': self.slides,
                'phase_reports': self.phase_reports,
                'feedback_history': self.feedback_history,
                'html_preview': self.html_preview,
                'pdf_generated': self.pdf_generated,
            }
            self.save_state()
            

            return True

        except Exception as e:
            print(f"Error loading state: {str(e)}")
            # st.error(f"Error loading state: {str(e)}")
            return False

    def save_slide(self, slide_type: str, content: Dict) -> bool:
        """Save slide content"""
        try:
            self.slides[slide_type] = content
            return self.save_state()
        except Exception as e:
            print(f"Error saving slide: {str(e)}")
            # st.error(f"Error saving slide: {str(e)}")
            return False

    def get_slide(self, slide_type: str) -> Optional[Dict]:
        """Get slide content"""
        return self.slides.get(slide_type)

    def add_feedback(self, slide_type: str, feedback: str) -> bool:
        """Add feedback for a slide"""
        try:
            if slide_type not in self.feedback_history:
                self.feedback_history[slide_type] = []

            self.feedback_history[slide_type].append({
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            })

            return self.save_state()
        except Exception as e:
            print(f"Error adding feedback: {str(e)}")
            return False

    def save_phase_report(self, phase: int, report: Dict) -> bool:
        """Save phase completion report"""
        try:
            self.phase_reports[str(phase)] = {
                'report': report,
                'timestamp': datetime.now().isoformat()
            }
            return self.save_state()
        except Exception as e:
            print(f"Error saving phase report: {str(e)}")
            # st.error(f"Error saving phase report: {str(e)}")
            return False

    def update_slide(self, slide_type: str, edit_request: str, current_content: str) -> bool:
        """Update a specific slide based on edit request"""
        try:
            # Determine language for message content
            selected_language = self.user['current_language']

            if selected_language == "no":
                # Norwegian prompt
                message_content = f"""Vennligst oppdater denne lysbilden basert på følgende forespørsel:

    Nåværende Innhold:
    {current_content}

    Redigeringsforespørsel:
    {edit_request}

    Vennligst behold samme format og struktur, men innlem de ønskede endringene."""
            else:
                # English prompt (default)
                message_content = f"""Please update this slide based on the following request:

    Current Content:
    {current_content}

    Edit Request:
    {edit_request}

    Please maintain the same format and structure, but incorporate the requested changes."""

            # Send message to OpenAI
            message = self.client.beta.threads.messages.create(
                thread_id= self.user['thread_id'],
                role="user",
                content=message_content
            )

            run = self.client.beta.threads.runs.create(
                thread_id=self.user['thread_id'],
                assistant_id="asst_uCXB3ZuddxaZZeEqPh8LZ5Zf"
            )

            # Wait for completion with status updates
            # with st.spinner("Updating slide..."):
            while run.status in ["queued", "in_progress"]:
                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.user,
                    run_id=run.id
                )

            if run.status == "completed":
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.user['thread_id']
                )
                response = messages.data[0].content[0].text.value

                # Update both raw response and parsed content
                # st.session_state.raw_responses[slide_type] = response
                self.user['raw_responses'][slide_type] = response
                # Store in vector store
                success = self.user['vector_store'].store_slide(
                    project_id=self.user['current_project_id'],
                    slide_type=slide_type,
                    content=response
                )

                if success:
                    return True

            return False

        except Exception as e:
            # st.error(f"Error updating slide: {str(e)}")
            return False