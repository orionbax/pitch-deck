import random

import requests
import streamlit as st
import pdfkit
from googleapiclient.http import MediaIoBaseDownload
from project_state import ProjectState
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from io import BytesIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Initialize the current language in session state if not already set
if 'current_language' not in st.session_state:
    st.session_state.current_language = 'no'  # Default to Norwegian

# Access the current language from session state
current_language = st.session_state.current_language

# Define language-specific page titles and icons
page_titles = {
    "en": "Pitch Deck Generator",
    "no": "Presentasjonsgenerator"
}

page_icons = {
    "en": "📊",
    "no": "📈"  # You can choose a different icon for Norwegian if desired
}

# Set the page configuration with language support
st.set_page_config(
    page_title=page_titles[current_language],
    page_icon=page_icons[current_language],
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS right after page config
st.markdown("""
    <style>
    /* General app styling */
    .stApp {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #2e2e2e !important;
        border-right: 1px solid #444 !important;
    }

    /* Header styling */
    header {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
    }

    /* Input fields styling */
    input, textarea, select, .stTextInput > div > div, .stTextArea > div > div, .stSelectbox > div > div {
        background-color: #3e3e3e !important;
        color: #e0e0e0 !important;
        border-color: #555 !important;
    }

    /* Dropdown menu styling */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #3e3e3e !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #3e3e3e !important;
    }
    .stSelectbox div[data-baseweb="select"] .css-1wa3eu0-placeholder {
        color: red !important;
    }
    .stSelectbox div[data-baseweb="select"] .css-1uccc91-singleValue {
        color: red !important;
    }

    /* Force dropdown options to have a dark background and red text */
    .stSelectbox div[data-baseweb="select"] .css-1n7v3ny-option {
        background-color: #3e3e3e !important;
        color: red !important;
    }
    .stSelectbox div[data-baseweb="select"] .css-1n7v3ny-option:hover {
        background-color: #555 !important;
    }

    /* Dropdown menu panel */
    .stSelectbox div[data-baseweb="select"] .css-1pahdxg-control {
        background-color: #3e3e3e !important;
        color: red !important;
    }

    /* Additional targeting for dropdown text */
    .stSelectbox div[data-baseweb="select"] .css-1okebmr-indicatorContainer {
        color: red !important;
    }
    .stSelectbox div[data-baseweb="select"] .css-1hb7zxy-IndicatorsContainer {
        color: red !important;
    }

    /* Button styling */
    .stButton button {
        background-color: #007acc !important;
        color: white !important;
        border: none !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        border-color: #555 !important;
    }

    /* Success/Info/Error message styling */
    .stSuccess, .stInfo, .stWarning, .stError {
        background-color: #3e3e3e !important;
        color: #e0e0e0 !important;
        border: 1px solid #555 !important;
    }

    /* Code blocks */
    .stCodeBlock {
        background-color: #2e2e2e !important;
    }

    /* Table styling */
    .stTable {
        background-color: #2e2e2e !important;
        color: #e0e0e0 !important;
    }

    /* Ensure all text is visible */
    p, span, div, h1, h2, h3, h4, h5, h6, li, label {
        color: #e0e0e0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Rest of your imports and code...

import os
from pathlib import Path
import time
import re
from vector_store import VectorStore
from datetime import datetime
import asyncio
from pathlib import Path
import PyPDF2
from dotenv import load_dotenv
import base64
from typing import Dict, List, Optional, Any
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from openai import OpenAI
import json
from messages import (
    PHASE_NAMES_ENGLISH, PHASE_NAMES_NORWEGIAN, PHASE_CONFIGS_ENGLISH, PHASE_CONFIGS_NORWEGIAN,EDITING_MODES, EXPORT_CONFIGS,
    SLIDE_TYPES_ENGLISH, SLIDE_TYPES_NORWEGIAN, LANGUAGE_CONFIGS, get_phase_names
)
import jinja2

import sys
import traceback

import uuid

# First Streamlit command must be set_page_config

# Load environment variables
load_dotenv()


from fastapi import FastAPI

app = FastAPI()




# Debug environment variables
# st.write("### Debugging Environment Variables")
# st.write(f"Current working directory: {Path('.env').absolute()}")
# st.write(f".env file exists: {Path('.env').exists()}")

# api_key = os.getenv('PINECONE_API_KEY')
# env = os.getenv('PINECONE_ENVIRONMENT')

# st.write("PINECONE_API_KEY:", "Set" if api_key else "Not Set")
# st.write("OPENAI_API_KEY:", "Set" if os.getenv('OPENAI_API_KEY') else "Not Set")
# st.write("PINECONE_ENVIRONMENT:", env if env else "Not Set")

# Rest of your imports

# ... rest of your code ...




class PitchDeckGenerator:
    def __init__(self, user):
        """Initialize the application"""
        self.init_session_state()
        self.setup_openai_client()
        self.setup_vector_store()
        # self.setup_templates()
        self.user = user

    def log_api_call(self, action: str, details: str, error: bool = False):
        """Log API calls and important events with enhanced error checking"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = "❌" if error else "✅"
            log_entry = f"[{timestamp}] {status} {action}: {details}"

            # Initialize logger if it doesn't exist
            if 'logger' not in self.user:
                self.user['logger'] = []

            # Check for 'setIn' related errors
            if "setIn' cannot be called on an ElementNode" in str(details):
                error_context = """
                Error: Attempted to modify a Streamlit element after rendering.
                This usually happens when trying to update UI elements outside the normal flow.
                Solution: Move the modification before the element is rendered.
                """
                log_entry += f"\nContext: {error_context}"
                st.error(error_context)

            self.user['logger'].append(log_entry)

            # Keep only last 100 entries
            if len(self.user['logger']) > 100:
                self.user['logger'] = self.user['logger'][-100:]

        except Exception as e:
            # st.error(f"Logging failed: {str(e)}") 
            pass # send a socket message to the client 'error': message

    def init_session_state(self):
        """Initialize all session state variables with error handling"""
        try:
            if 'initialized' not in self.user:
                self.user['initialized'] = False

            if not self.user.get('initialized', None):
                session_vars = {
                    'current_project_id': None,
                    'project_state': None,
                    'thread_id': None,
                    'files_uploaded': False,
                    'document_cache': {},
                    'logger': [],
                    'error_log': [],
                    'chat_history': [],
                    'should_rerun': False,
                    'editing_mode': 'structured',
                    'current_slide': None,
                    'preview_html': None,
                    'active_tab': "Documents",  # Initialize active_tab
                    'current_tab': 0,  # Initialize current_tab
                    'last_error': None,
                    'system_messages': []
                }

                for var, value in session_vars.items():
                    if var not in self.user:
                        self.user[var] = value

                self.user['initialized'] = True
                self.log_api_call("Initialization", "Session state initialized successfully")

        except Exception as e:
            self.log_error(e, "Session State Initialization")
            st.error("Failed to initialize session state. Please refresh the page.")

    def setup_openai_client(self):
        """Initialize OpenAI client"""
        try:
            if 'client' not in st.session_state:
                self.user['client'] = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                self.log_api_call("Initialization", "OpenAI client initialized")
        except Exception as e:
            self.log_api_call("Error", f"OpenAI client initialization failed: {str(e)}", error=True)
            raise

    def setup_vector_store(self):
        """Initialize vector store"""
        try:
            api_key = os.getenv('PINECONE_API_KEY')
            environment = "gcp-starter"

            if not api_key:
                # st.error("Missing required environment variables")
                # st.error("Please check your .env file for PINECONE_API_KEY")
                # st.stop()
                self.log_api_call("Error", "Missing required environment variables", error=True)
            if 'vector_store' not in self.user:
                self.user['vector_store'] = VectorStore(
                    api_key=api_key,
                    environment=environment,
                    log_function=self.log_api_call
                )
                self.log_api_call("Initialization", "Vector store initialized")

        except Exception as e:
            # st.error(f"Failed to initialize vector store: {str(e)}")
            # st.error("Please verify your Pinecone API key and environment settings")
            # raise
            self.log_api_call("Error", f"Failed to initialize vector store: {str(e)}", error=True)

    def setup_templates(self):
        """Initialize Jinja2 templates"""
        try:
            # Create templates directory if it doesn't exist
            templates_dir = Path('templates')
            templates_dir.mkdir(exist_ok=True)

            # Initialize Jinja2 environment
            self.template_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader('templates'),
                autoescape=True
            )

            # Create default template if it doesn't exist
            default_template_path = templates_dir / 'pitch_deck.html'
            if not default_template_path.exists():
                default_template = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Pitch Deck</title>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        .slide { margin: 20px; padding: 20px; border: 1px solid #ccc; }
                        .slide-title { font-size: 24px; margin-bottom: 15px; }
                        .slide-content { font-size: 16px; }
                    </style>
                </head>
                <body>
                    {% for slide_type, content in slides.items() %}
                  <div class="slide">
    <div class="slide-title">{{ slide_type }}</div>
    
</div>


                    {% endfor %}
                </body>
                </html>
                """
                with open(default_template_path, 'w') as f:
                    f.write(default_template)

            self.log_api_call("Initialization", "Templates initialized")

        except Exception as e:
            error_msg = f"Template initialization failed: {str(e)}"
            self.log_api_call("Error", error_msg, error=True)
            raise Exception(error_msg)

    def sidebar_content(self):
        """Display sidebar content and controls with error checking"""
        if not self.check_ui_modifications():
            return

        try:
            st.sidebar.title("Pitch Deck Generator")

            # Language selector
            st.sidebar.markdown("### Language")
            selected_language = st.sidebar.selectbox(
                "Select Language",
                options=list(LANGUAGE_CONFIGS.keys()),
                format_func=lambda x: LANGUAGE_CONFIGS[x]['name'],
                index=0 if self.current_language == "no" else 1
            )

            if selected_language != self.current_language:
                self.current_language = selected_language
                self.save_state()
                st.rerun()

            # Editing mode selector
            st.sidebar.markdown("### Editing Mode")
            editing_mode = st.sidebar.radio(
                "Select editing mode",
                options=list(EDITING_MODES.keys()),
                format_func=lambda x: EDITING_MODES[x]['name']
            )

            if editing_mode != self.editing_mode:
                self.editing_mode = editing_mode
                st.rerun()

            # Progress tracking
            if self.current_phase:
                st.sidebar.markdown("### Progress")
                progress = st.sidebar.progress(0)
                current_phase = self.current_phase
                total_phases = len(get_phase_names(self.current_language))
                progress.progress(current_phase / total_phases)

                phase_names = get_phase_names(self.current_language)
                st.sidebar.markdown(f"**Current Phase:** {phase_names[current_phase]}")

            # Console output
            self.display_console()

        except Exception as e:
            if "setIn' cannot be called on an ElementNode" in str(e):
                st.error("""
                UI Modification Error:
                Cannot modify elements after they're rendered.
                Please refresh the page and try again.
                """)
                self.log_error(e, "Sidebar Content - ElementNode Error")
            else:
                self.log_error(e, "Sidebar Content")

    def display_console(self):
        """Display console output with enhanced error detection"""
        try:
            if st.sidebar.checkbox("Show Console Output", value=False):
                st.sidebar.markdown("### Console Output")

                # Add error detection for ElementNode issues
                element_node_errors = [
                    log for log in st.session_state.get('logger', [])
                    if "setIn' cannot be called on an ElementNode" in log
                ]

                if element_node_errors:
                    st.sidebar.error("""
                    ElementNode Error Detected!
                    Common causes:
                    1. Modifying UI elements after they're rendered
                    2. Incorrect state management
                    3. Async operations affecting UI
                    
                    Try:
                    1. Moving state modifications earlier in the code
                    2. Using st.session_state for state management
                    3. Ensuring all UI updates happen in the main flow
                    """)

                # Add system info
                st.sidebar.markdown("#### System Information")
                st.sidebar.code(f"""
Python Version: {sys.version}
Streamlit Version: {st.__version__}
Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """)

                # Add session state debug info
                st.sidebar.markdown("#### Session State")
                st.sidebar.code(f"""
Initialized: {st.session_state.get('initialized', False)}
Current Phase: {self.current_phase if hasattr(self, 'current_phase') else 'Not Set'}
Files Uploaded: {st.session_state.get('files_uploaded', False)}
Current Tab: {st.session_state.get('active_tab', 'Not Set')}
                """)

                # Add error log section
                st.sidebar.markdown("#### Error Log")
                if 'error_log' not in st.session_state:
                    st.session_state.error_log = []

                for error in st.session_state.error_log[-5:]:  # Show last 5 errors
                    st.sidebar.error(error)

                # Add general log section
                st.sidebar.markdown("#### General Log")
                if 'logger' in st.session_state and st.session_state.logger:
                    for log in reversed(st.session_state.logger[-10:]):  # Show last 10 entries
                        st.sidebar.text(log)
                else:
                    st.sidebar.text("No console output available")

        except Exception as e:
            self.log_error(e, "Console Display")

    def log_error(self, error: Exception, context: str = ""):
        """Enhanced error logging function"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_msg = f"""
[{timestamp}] ERROR in {context}
Type: {type(error).__name__}
Message: {str(error)}
Traceback:
{traceback.format_exc()}
Session State Keys: {list(st.session_state.keys())}
        """

        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
        st.session_state.error_log.append(error_msg)

        # Also log to standard logger
        self.log_api_call("Error", error_msg, error=True)

    def display_html_preview(self):
        """Display HTML preview of the pitch deck"""
        if not self.slides:
            st.info("No slides to preview yet. Create some slides first!")
            return

        try:
            # Get the template
            template = self.template_env.get_template('pitch_deck.html')

            # Render the template with current slides
            html_content = template.render(
                slides=self.slides,
                language=self.current_language,
                configs={
                    'slides': SLIDE_TYPES_ENGLISH,
                    'language': LANGUAGE_CONFIGS
                }
            )

            # Store the preview
            if self.vector_store.store_html_preview(
                    self.current_project_id,
                    html_content
            ):
                self.html_preview = html_content

                # Display preview
                st.components.v1.html(
                    html_content,
                    height=600,
                    scrolling=True
                )

                # Download button
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("Export as PDF"):
                        pdf_buffer = generate_pdf_from_text(st.session_state.project_state.slides)
                        st.download_button(
                            "Download PDF",
                            data=pdf_buffer,
                            file_name="pitch_deck.pdf",
                            mime="application/pdf"
                        )

                with col2:
                    if st.button("Export as HTML"):
                        if st.session_state.project_state.html_preview:
                            st.download_button(
                                "Download HTML",
                                st.session_state.project_state.html_preview,
                                file_name="pitch_deck.html",
                                mime="text/html"
                            )

                with col3:
                    if st.button("Export to Google Slides"):
                        # Trigger the Google Slides export function
                        export_to_google_slides(st.session_state.project_state.slides)
                        st.success("Pitch deck exported to Google Slides successfully!")
                    self.log_api_call("Export", "HTML preview downloaded")

            else:
                st.error("Failed to generate preview")

        except Exception as e:
            st.error(f"Error generating preview: {str(e)}")
            self.log_api_call("Error", f"Preview generation failed: {str(e)}", error=True)

    # Add this helper method to check for UI modification issues
    def check_ui_modifications(self):
        """Check for potential UI modification issues"""
        try:
            if hasattr(st.session_state, '_is_rendering'):
                st.warning("""
                Potential UI modification during rendering detected.
                This might cause 'setIn' ElementNode errors.
                Please ensure all state modifications happen before rendering UI elements.
                """)
                return False
            return True
        except Exception as e:
            self.log_error(e, "UI Modification Check")
            return False

# Unwanted
def handle_preview_tab():
    """Handle Preview tab content"""

    # Access the current language from session state
    current_language = st.session_state.current_language

    # Define language-specific text
    header_text = {
        "en": "Preview Pitch Deck",
        "no": "Forhåndsvisning av presentasjon"
    }

    no_slides_text = {
        "en": "No slides to preview yet. Create some slides first!",
        "no": "Ingen lysbilder å forhåndsvise ennå. Lag noen lysbilder først!"
    }

    export_pdf_button = {
        "en": "Export as PDF",
        "no": "Eksporter som PDF"
    }

    download_pdf_button = {
        "en": "Download PDF",
        "no": "Last ned PDF"
    }

    export_html_button = {
        "en": "Export as HTML",
        "no": "Eksporter som HTML"
    }

    download_html_button = {
        "en": "Download HTML",
        "no": "Last ned HTML"
    }

    export_google_slides_button = {
        "en": "Export to Google Slides",
        "no": "Eksporter til Google Slides"
    }

    export_success_text = {
        "en": "Pitch deck exported to Google Slides successfully!",
        "no": "Presentasjonen ble eksportert til Google Slides!"
    }

    html_download_success_text = {
        "en": "HTML file downloaded successfully!",
        "no": "HTML-filen ble lastet ned!"
    }

    st.header(header_text[current_language])

    if not st.session_state.project_state.slides:
        st.info(no_slides_text[current_language])
        return

    try:
        # Create simple HTML content with white text and proper encoding
        html_content = """
        <!DOCTYPE html>
        <html lang="no">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    background-color: #0e1117;
                    color: white;
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }
                .slide {
                    margin-bottom: 40px;
                    color: white;
                }
                .slide-title {
                    color: white;
                    font-size: 24px;
                    margin-bottom: 15px;
                    border-bottom: 1px solid #ffffff40;
                    padding-bottom: 10px;
                }
                .slide-content {
                    color: white;
                    font-size: 16px;
                    line-height: 1.5;
                    padding-left: 20px;
                }
                .bullet-point {
                    color: white;
                    margin-bottom: 8px;
                    padding-left: 15px;
                    position: relative;
                }
                .bullet-point:before {
                    content: "•";
                    position: absolute;
                    left: 0;
                    color: white;
                }
                .introduction-text {
                    color: white;
                    font-size: 16px;
                    line-height: 1.6;
                    padding-left: 20px;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
        """
        selected_slide_types = {
            k: v for k, v in (
                SLIDE_TYPES_NORWEGIAN if st.session_state.current_language == 'no' else SLIDE_TYPES_ENGLISH).items()
            if k in st.session_state.selected_slides and st.session_state.selected_slides[k]
        }
        # Add each slide's content
        for slide_type, slide_data in st.session_state.project_state.slides.items():
            slide_config = selected_slide_types.get(slide_type, {})
            slide_name = slide_config.get('name', slide_type.title())

            html_content += f'<div class="slide"><div class="slide-title">{slide_name}</div>'

            if slide_type == 'introduction':
                # Special handling for introduction slide - paragraph format
                if slide_type in st.session_state.get('raw_responses', {}):
                    content = st.session_state.raw_responses[slide_type]
                    # Clean the content
                    content = content.replace('**', '').strip()
                    html_content += f'<div class="introduction-text">{content}</div>'
            else:
                # Regular bullet point format for other slides
                html_content += '<div class="slide-content">'
                if slide_type in st.session_state.get('raw_responses', {}):
                    content = st.session_state.raw_responses[slide_type]
                    for line in content.split('\n'):
                        if line.strip():
                            # Clean the line
                            line = line.replace('**', '').strip()
                            if line.startswith('- '):
                                line = line[2:]
                            html_content += f'<div class="bullet-point">{line}</div>'
                html_content += '</div>'

            html_content += '</div>'

        html_content += """
        </body>
        </html>
        """

        # Display preview
        st.components.v1.html(
            html_content,
            height=600,
            scrolling=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(export_pdf_button[current_language]):
                pdf_buffer = generate_pdf_from_text(st.session_state.project_state.slides)
                st.download_button(
                    download_pdf_button[current_language],
                    data=pdf_buffer,
                    file_name="pitch_deck.pdf",
                    mime="application/pdf"
                )

        with col2:
            if st.button(export_html_button[current_language]):
                if st.session_state.project_state.html_preview:
                    st.download_button(
                        download_html_button[current_language],
                        st.session_state.project_state.html_preview,
                        file_name="pitch_deck.html",
                        mime="text/html"
                    )

        with col3:
            if st.button(export_google_slides_button[current_language]):
                # Trigger the Google Slides export function
                export_to_google_slides(st.session_state.project_state.slides)
                st.success(export_success_text[current_language])
            st.success(html_download_success_text[current_language])

    except Exception as e:
        st.error(f"Error generating preview: {str(e)}")


# To be used
def draw_text_paragraph(c, text, y_position, x_position, max_width, font="Helvetica", font_size=10, line_height=14):
    """
    Draws a text paragraph within specified width, handling line wrapping.
    Returns the updated y_position after drawing the text.
    """
    c.setFont(font, font_size)
    words = text.split()
    line = ""

    for word in words:
        # Check if adding the next word would exceed max width
        if stringWidth(line + word, font, font_size) <= max_width:
            line += f"{word} "
        else:
            # Draw the current line and reset
            c.drawString(x_position, y_position, line.strip())
            y_position -= line_height
            line = f"{word} "

    # Draw the last line if there is any leftover text
    if line:
        c.drawString(x_position, y_position, line.strip())
        y_position -= line_height

    return y_position

#To be used
def generate_pdf_from_text(slides):
    """Generate a PDF document from text content, with each slide on a new page and adjusted formatting."""
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    margin = 60  # Increased margin for better readability
    y_position_start = height - margin

    # Set default font sizes
    title_font_size = 20  # Smaller but still prominent
    text_font_size = 10  # Smaller for body text
    line_height = 14  # Adjusted line height for readability

    first_page = True  # Track if it's the first page



    # Now access current_language from the instance
    selected_language = st.session_state.project_state.current_language
    bullet_symbol = "•" if selected_language == "en" else "-"  # Choose bullet symbol based on language

    # Loop through slides and add content
    for slide_type, slide_data in slides.items():
        if not first_page:
            c.showPage()  # Start each slide on a new page
        else:
            first_page = False  # Skip creating a new page for the first slide
        y_position = y_position_start

        # Retrieve slide configurations and title based on language
        slide_config = SLIDE_TYPES_ENGLISH.get(slide_type, {})
        slide_name = slide_config.get('name', slide_type.title())

        # Language-specific titles (if needed)
        if selected_language == "Norwegian":
            if slide_type == "introduction":
                slide_name = "Introduksjon"
            # Add other language-based title mappings here as needed

        # Draw slide title
        c.setFont("Helvetica-Bold", title_font_size)
        c.drawString(margin, y_position, slide_name)
        y_position -= title_font_size + 12  # Space after title

        # Language-specific content processing
        if slide_type == 'introduction':
            # Introduction slide with paragraph format
            content = st.session_state.raw_responses.get(slide_type, '').replace('**', '').strip()
            y_position = draw_text_paragraph(
                c, content, y_position, margin, width - 2 * margin,
                font="Helvetica", font_size=text_font_size, line_height=line_height
            )
        else:
            # Bullet point format for other slides
            content = st.session_state.raw_responses.get(slide_type, '')
            for line in content.split('\n'):
                if line.strip():
                    line = line.replace('**', '').strip()
                    if line.startswith('- '):
                        line = line[2:]

                    # Adjust x position and max width for bullet points
                    bullet_indent = margin + 10
                    bullet_width = width - 2 * margin - 20
                    c.setFont("Helvetica", text_font_size)
                    y_position = draw_text_paragraph(
                        c, f"{bullet_symbol} {line}", y_position, bullet_indent, bullet_width,
                        font="Helvetica", font_size=text_font_size, line_height=line_height
                    )

        y_position -= 30  # Space between slides

        # Ensure we avoid overflow by creating a new page if needed
        if y_position < margin:
            c.showPage()
            y_position = y_position_start

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

# Unwanted
def handle_export_tab():
    """Handle Export tab content with additional Google Slides export option."""
    st.header("Export Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Export as PDF"):
            pdf_buffer = generate_pdf_from_text(st.session_state.project_state.slides)
            st.download_button(
                "Download PDF",
                data=pdf_buffer,
                file_name="pitch_deck.pdf",
                mime="application/pdf"
            )

    with col2:
        if st.button("Export as HTML"):
            if st.session_state.project_state.html_preview:
                st.download_button(
                    "Download HTML",
                    st.session_state.project_state.html_preview,
                    file_name="pitch_deck.html",
                    mime="text/html"
                )

    with col3:
        if st.button("Export to Google Slides"):
            # Trigger the Google Slides export function
            export_to_google_slides(st.session_state.project_state.slides)
            st.success("Pitch deck exported to Google Slides successfully!")


# def load_css():
#     st.markdown("""
#     <style>
#         /* Apply red color to all text elements */
#           div   {
#             color: red !important;
#         }
        
#     </style>
#     """, unsafe_allow_html=True)



from urllib.parse import quote
# TO be used
def extract_keywords(text, max_words=3):
    # Use a simple regex to extract words longer than 3 characters, which are likely to be more descriptive
    words = re.findall(r'\b\w{4,}\b', text)
    # Limit the number of keywords to avoid overly long URLs
    keywords = ' '.join(words[:max_words])
    return keywords

# To be used
def generate_image_url(title, body):
    # Refine search for high-quality, dark-themed images with sharp resolution
    combined_keywords = f"{extract_keywords(title)} {extract_keywords(body)} dark moody night high resolution sharp clear".strip()

    headers = {
        "Authorization": "Pp6TvyGBYUcRlpWzdShoAExfMntaCj1UA1UQuz0vz5mYQHViak60S2ub"  # Replace with your Pexels API key
    }

    response = requests.get(f"https://api.pexels.com/v1/search?query={combined_keywords}&per_page=1", headers=headers)

    if response.status_code == 200 and response.json().get('photos'):
        # Choose 'large' for better quality without being too large
        return response.json()['photos'][0]['src']['large']  # 'large' is a good compromise between quality and size

    # Fallback to a default image if no result is found
    return "https://www.example.com/default-dark-image.jpg"  # Replace with your fallback image URL

# Use this in your Google Slides export function

# To be used
def export_to_google_slides(slides):
    # Authenticate and initialize the Google Slides API service with necessary scopes
    creds = service_account.Credentials.from_service_account_file(
        "psychic-trainer-378112-7d76d802092f.json",
        scopes=["https://www.googleapis.com/auth/presentations", "https://www.googleapis.com/auth/drive"]
    )
    slides_service = build("slides", "v1", credentials=creds)

    # Create a new presentation
    presentation = slides_service.presentations().create(body={"title": st.session_state.project_name}).execute()
    presentation_id = presentation.get("presentationId")
    print(f"Created presentation with ID: {presentation_id}")

    # Format slides for Google Slides
    for slide_type, slide_data in slides.items():
        slide_content = st.session_state.raw_responses.get(slide_type, "")
        print(f"Slide Type: {slide_type}, Content: {slide_content}")

        # Step 1: Create a new slide with TITLE_AND_BODY layout
        create_slide_response = slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={
                "requests": [
                    {
                        "createSlide": {
                            "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"}
                        }
                    }
                ]
            }
        ).execute()
        print("Create Slide Response:", json.dumps(create_slide_response, indent=2))

        # Retrieve the page ID of the newly created slide
        page_id = create_slide_response['replies'][0]['createSlide']['objectId']
        print(f"Created slide with page ID: {page_id}")

        title_text = slide_data.get('title', slide_type.title())
        image_url = generate_image_url(title_text, slide_content)

        # Step 2: Set the image as the slide background
        if image_url:
            slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={
                    "requests": [
                        {
                            "updatePageProperties": {
                                "objectId": page_id,
                                "pageProperties": {
                                    "pageBackgroundFill": {
                                        "stretchedPictureFill": {
                                            "contentUrl": image_url
                                        }
                                    }
                                },
                                "fields": "pageBackgroundFill"
                            }
                        }
                    ]
                }
            ).execute()

        # Step 3: Retrieve placeholders for title and body text boxes
        slide = slides_service.presentations().pages().get(
            presentationId=presentation_id,
            pageObjectId=page_id
        ).execute()
        print("Slide Structure:", json.dumps(slide, indent=2))

        title_id, body_id = None, None
        for element in slide.get('pageElements', []):
            element_id = element.get('objectId', '')
            placeholder_info = element.get('shape', {}).get('placeholder', {})
            placeholder_type = placeholder_info.get('type', '')

            if placeholder_type == "TITLE":
                title_id = element_id
            elif placeholder_type == "BODY":
                body_id = element_id

        # Step 4: Insert text into placeholders and update text color
        requests = []
        if title_id:
            # Insert title text
            requests.append({
                "insertText": {
                    "objectId": title_id,
                    "text": title_text
                }
            })
            # Set title text color to white
            requests.append({
                "updateTextStyle": {
                    "objectId": title_id,
                    "style": {
                        "foregroundColor": {
                            "opaqueColor": {
                                "rgbColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                            }
                        }
                    },
                    "textRange": {"type": "ALL"},
                    "fields": "foregroundColor"
                }
            })

        if body_id:
            # Insert body text
            requests.append({
                "insertText": {
                    "objectId": body_id,
                    "text": slide_content
                }
            })
            # Set body text color to white
            requests.append({
                "updateTextStyle": {
                    "objectId": body_id,
                    "style": {
                        "foregroundColor": {
                            "opaqueColor": {
                                "rgbColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                            }
                        }
                    },
                    "textRange": {"type": "ALL"},
                    "fields": "foregroundColor"
                }
            })

        # Execute the batch update to insert text and apply white color styling
        if requests:
            slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": requests}
            ).execute()

    st.write(f"Exported to Google Slides: {presentation_id}")


    drive_service = build('drive', 'v3', credentials=creds)


    file_format = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'  # PowerPoint (.pptx)
    request = drive_service.files().export_media(
        fileId=presentation_id,
        mimeType=file_format
    )


    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download progress: {int(status.progress() * 100)}%")
    fh.seek(0)


    st.download_button(
        label="Download Pitch Deck (PowerPoint)",
        data=fh,
        file_name=f"{st.session_state.project_name}_pitch_deck.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )



# Unwanted
def main():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

    if 'current_project_id' not in st.session_state or not st.session_state.current_project_id:
        # Language-specific welcome message
        welcome_message = {
            "en": "Welcome to Pitch Deck Generator",
            "no": "Velkommen til Pitch Deck Generator"
        }
        st.title(welcome_message[current_language])

        # Language-specific project name prompt
        project_name_prompt = {
            "en": "Enter your project name:",
            "no": "Skriv inn prosjektnavnet ditt:"
        }
        project_name = st.text_input(project_name_prompt[current_language])
        
        if project_name:
            st.session_state.current_project_id = str(uuid.uuid4())
            st.session_state.project_name = project_name
            st.session_state.initialized = False
            st.rerun()
        st.stop()

    # load_css()

    if not st.session_state.initialized:
        if 'vector_store' not in st.session_state:
            api_key = os.getenv('PINECONE_API_KEY')
            environment = "gcp-starter"

            def log_function(action: str, details: str, error: bool = False):
                if error:
                    st.error(f"{action}: {details}")
                else:
                    st.write(f"{action}: {details}")

            st.session_state.vector_store = VectorStore(
                api_key=api_key,
                environment=environment,
                log_function=log_function
            )

        if 'project_state' not in st.session_state:
            st.session_state.project_state = ProjectState(
                st.session_state.current_project_id,
                st.session_state.vector_store
            )
            st.session_state.project_state.load_state()

        session_vars = {
            'thread_id': None,
            'files_uploaded': False,
            'document_cache': {},
            'logger': [],
            'error_log': [],
            'chat_history': [],
            'should_rerun': False,
            'editing_mode': 'structured',
            'current_slide': None,
            'preview_html': None,
            'active_tab': "Documents",
            'current_tab': 0,
            'last_error': None,
            'system_messages': [],
            'current_language': st.session_state.project_state.current_language if hasattr(
                st.session_state.project_state, 'current_language') else 'no',
            'upload_state': {
                'files_processed': [],
                'processing_complete': False
            }
        }

        for var, value in session_vars.items():
            if var not in st.session_state:
                st.session_state[var] = value

        st.session_state.initialized = True

    app = PitchDeckGenerator()

    st.sidebar.title("Pitch Deck Generator")

    # Language-specific project label
    project_label = {
        "en": "Project",
        "no": "Prosjekt"
    }
    st.sidebar.markdown(f"### {project_label[current_language]}: {st.session_state.project_name}")

    # Language selector
    st.sidebar.markdown("### Language")
    selected_language = st.sidebar.selectbox(
        "Select Language",
        options=list(LANGUAGE_CONFIGS.keys()),
        format_func=lambda x: LANGUAGE_CONFIGS[x]['name'],
        index=list(LANGUAGE_CONFIGS.keys()).index(current_language)
    )

    if selected_language != current_language:
        st.session_state.current_language = selected_language
        st.session_state.project_state.current_language = selected_language
        st.session_state.project_state.save_state()
        st.rerun()

    # Language-specific editing mode label
    editing_mode_label = {
        "en": "Editing Mode",
        "no": "Redigeringsmodus"
    }
    st.sidebar.markdown(f"### {editing_mode_label[current_language]}")
    editing_mode = st.sidebar.radio(
        "Select editing mode",
        options=list(EDITING_MODES.keys()),
        format_func=lambda x: EDITING_MODES[x]['name']
    )

    if editing_mode != st.session_state.editing_mode:
        st.session_state.editing_mode = editing_mode
        st.rerun()

    if st.session_state.project_state and hasattr(st.session_state.project_state, 'current_phase'):
        # Language-specific progress label
        progress_label = {
            "en": "Progress",
            "no": "Fremdrift"
        }
        st.sidebar.markdown(f"### {progress_label[current_language]}")
        progress = st.sidebar.progress(0)
        current_phase = st.session_state.project_state.current_phase
        total_phases = len(get_phase_names(current_language))
        progress.progress(current_phase / total_phases)

        phase_names = get_phase_names(current_language)
        st.sidebar.markdown(f"**Current Phase:** {phase_names[current_phase]}")

    # Language-specific console output label
    console_output_label = {
        "en": "Console Output",
        "no": "Konsollutdata"
    }
    if st.sidebar.checkbox(console_output_label[current_language], value=False):
        st.sidebar.markdown(f"### {console_output_label[current_language]}")
        if 'logger' in st.session_state and st.session_state.logger:
            for log in reversed(st.session_state.logger[-10:]):
                st.sidebar.text(log)
        else:
            st.sidebar.text("No console output available")

    # Language-specific navigation label
    navigation_label = {
        "en": "Navigation",
        "no": "Navigasjon"
    }
    st.sidebar.markdown(f"### {navigation_label[current_language]}")
    selected_tab = st.sidebar.radio(
        "Select Section",
        ["Documents", "Slides", "Preview", "Export"],
        key="navigation",
        index=["Documents", "Slides", "Preview", "Export"].index(st.session_state.active_tab)
    )

    if selected_tab == "Documents":
        handle_documents_tab()
    elif selected_tab == "Slides":
        handle_slides_tab()
    elif selected_tab == "Preview":
        handle_preview_tab()
    elif selected_tab == "Export":
        handle_export_tab()

# Unwanted
def handle_documents_tab():
    """Handle Documents tab content"""
    # Access the current language from session state
    current_language = st.session_state.current_language

    # Define language-specific text
    header_text = {
        "en": "Upload Documents",
        "no": "Last opp dokumenter"
    }

    upload_prompt = {
        "en": "Upload company documents",
        "no": "Last opp selskapsdokumenter"
    }

    processing_message = {
        "en": "Processing documents...",
        "no": "Behandler dokumenter..."
    }

    processed_message = {
        "en": "Documents processed:",
        "no": "Dokumenter behandlet:"
    }

    complete_upload_button = {
        "en": "Complete Document Upload",
        "no": "Fullfør dokumentopplasting"
    }

    upload_more_button = {
        "en": "Upload More Documents",
        "no": "Last opp flere dokumenter"
    }

    move_to_slides_message = {
        "en": "Moving to Slides section...",
        "no": "Går til lysbilde-seksjonen..."
    }

    st.header(header_text[current_language])

    # Initialize upload state if needed
    if 'upload_state' not in st.session_state:
        st.session_state.upload_state = {
            'files_processed': [],
            'processing_complete': False
        }

    # Now we can safely access current_phase
    if not st.session_state.upload_state['processing_complete']:
        uploaded_files = st.file_uploader(
            upload_prompt[current_language],
            accept_multiple_files=True,
            type=['txt', 'pdf', 'doc', 'docx'],
            key="document_uploader"
        )

        # Process files only if new ones are uploaded
        if uploaded_files:
            new_files = [f for f in uploaded_files if f.name not in st.session_state.upload_state['files_processed']]

            if new_files:
                progress_container = st.empty()
                with progress_container.container():
                    with st.spinner(processing_message[current_language]):
                        for file in new_files:
                            try:
                                if handle_document_upload(file):
                                    st.session_state.upload_state['files_processed'].append(file.name)
                                    st.success(f"✅ Processed: {file.name}")
                            except Exception as e:
                                st.error(f"❌ Error processing {file.name}: {str(e)}")

        # Display processed files
        if st.session_state.upload_state['files_processed']:
            st.success(f"🎉 {processed_message[current_language]}")
            for file_name in st.session_state.upload_state['files_processed']:
                st.write(f"✅ {file_name}")

            if st.button(complete_upload_button[current_language], type="primary"):
                st.session_state.upload_state['processing_complete'] = True
                st.session_state.project_state.current_phase = 1  # Set to Slide Planning phase
                st.session_state.project_state.save_state()
                st.success(move_to_slides_message[current_language])
                st.session_state.active_tab = "Slides"
                st.rerun()
    else:
        # Show completed state
        st.success(f"🎉 {processed_message[current_language]}")
        for file_name in st.session_state.upload_state['files_processed']:
            st.write(f"✅ {file_name}")

        if st.button(upload_more_button[current_language]):
            st.session_state.upload_state['processing_complete'] = False
            st.rerun()


# TO be used
def parse_slide_response(response: str, slide_type:  str) -> dict:
    """Parse the AI's rich response into structured slide content."""
    try:
        # Set up data structure
        slide_content = {
            "sections": {
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "references": [],
                "metrics": [],
                "sources": []
            }
        }

        # Unwanted phrases to filter out
        unwanted_phrases = ["Title Slide", "For the Title Slide", "Here's how you can structure it"]
        in_main_content = False
        main_content = []

        for line in str(response).split('\n'):
            line = line.strip()
            if not line:
                continue

            # Remove citation format and other unwanted symbols or bracketed text like 【】
            line = re.sub(r'【[^】]+】', '', line)  # Removes any citation in the format

            line = re.sub(r'\[[^\]]+\]|\【[^】]+】', '', line)
            # Skip lines containing any unwanted phrases
            if any(phrase in line for phrase in unwanted_phrases):
                continue



            # Skip lines starting with `##` or `###`
            if line.startswith('##') or line.startswith('###'):
                continue

            # Handle the '--' markers for main content collection
            if line == '--':
                in_main_content = not in_main_content  # Toggle in_main_content
                continue

            # Collect lines that are part of the main content
            if in_main_content:
                main_content.append(line)

        # Add the collected main content to the slide content
        slide_content["sections"]["main_content"] = {
            "content": [{"type": "simple", "content": item} for item in main_content]
        }

        return slide_content

    except Exception as e:
        print(f"Error parsing slide response: {str(e)}")  # For debugging purposes
        return {}


# Unwanted
def display_slide_content(slide_type: str, content: str):
    """Display slide content with edit functionality"""
    slide_config = SLIDE_TYPES_ENGLISH.get(slide_type, {})

    # Display slide title and content
    st.subheader(slide_config.get('name', slide_type.title()))

    # Get the raw response text from session state
    if slide_type in st.session_state.get('raw_responses', {}):
        slide_text = st.session_state.raw_responses[slide_type]
        st.markdown(slide_text)
    else:
        st.markdown(content)

    # Initialize edit state for this slide if not exists
    if f"editing_{slide_type}" not in st.session_state:
        st.session_state[f"editing_{slide_type}"] = False

    # Add edit button or show edit interface
    if not st.session_state[f"editing_{slide_type}"]:
        if st.button("✏️ Edit", key=f"edit_btn_{slide_type}"):
            st.session_state[f"editing_{slide_type}"] = True
            st.rerun()
    else:
        edit_request = st.text_area(
            "What changes would you like to make?",
            key=f"edit_{slide_type}"
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Cancel", key=f"cancel_{slide_type}"):
                st.session_state[f"editing_{slide_type}"] = False
                st.rerun()
        with col2:
            if st.button("Update", key=f"update_{slide_type}"):
                if edit_request:
                    try:
                        success = st.session_state.project_state.update_slide(
                            slide_type=slide_type,
                            edit_request=edit_request,
                            current_content=st.session_state.raw_responses[slide_type]
                        )
                        if success:
                            st.session_state[f"editing_{slide_type}"] = False
                            st.success("✨ Updated!")
                            st.rerun()
                        else:
                            st.error("Update failed. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Partially wanted: Use the error and success messages
def handle_document_upload(uploaded_file):
    """Handle document upload with proper tracking"""
    # Access the current language from session state
    current_language = st.session_state.current_language

    # Define language-specific messages
    extraction_failure_message = {
        "en": f"Failed to extract content from {uploaded_file.name}",
        "no": f"Kunne ikke hente innhold fra {uploaded_file.name}"
    }

    upload_success_message = {
        "en": f"Successfully uploaded {uploaded_file.name}",
        "no": f"Vellykket opplasting av {uploaded_file.name}"
    }

    store_failure_message = {
        "en": f"Failed to store {uploaded_file.name}",
        "no": f"Kunne ikke lagre {uploaded_file.name}"
    }

    error_processing_message = {
        "en": "Error processing upload",
        "no": "Feil ved behandling av opplasting"
    }

    try:
        content = st.session_state.vector_store._extract_content(uploaded_file)
        if not content:
            st.error(extraction_failure_message[current_language])
            return False

        # Prepare metadata
        metadata = {
            'filename': uploaded_file.name,
            'file_type': uploaded_file.type,
            'upload_time': datetime.now().isoformat()
        }

        # Store document with tracking
        success = st.session_state.vector_store.store_document(
            project_id=st.session_state.current_project_id,
            content=content,
            metadata=metadata
        )

        if success:
            st.success(upload_success_message[current_language])
            return True
        else:
            st.error(store_failure_message[current_language])
            return False

    except Exception as e:
        st.error(f"{error_processing_message[current_language]}: {str(e)}")
        return False

# Unwanted
def verify_project_state():
    """Verify and recover project state if needed"""
    try:
        if not hasattr(st.session_state.project_state, 'slides'):
            st.session_state.project_state.slides = {}

        if not hasattr(st.session_state.project_state, 'current_phase'):
            st.session_state.project_state.current_phase = 0


        for slide_type in SLIDE_TYPES_ENGLISH.keys():
            if slide_type not in st.session_state.project_state.slides:
                st.session_state.project_state.slides[slide_type] = {}

        st.session_state.project_state.save_state()
        return True
    except Exception as e:
        st.error(f"Failed to verify project state: {str(e)}")
        return False


# Unwanted: its frontend stuff
def handle_slides_tab():
    """Handle Slides tab content"""
    # Access the current language from session state
    current_language = st.session_state.current_language

    # Define language-specific text
    header_text = {
        "en": "Create Your Pitch Deck",
        "no": "Lag din presentasjon"
    }

    debug_info_text = {
        "en": "Show Debug Info",
        "no": "Vis feilsøkingsinformasjon"
    }

    document_analysis_prompt = {
        "en": "Please complete the document analysis phase first.",
        "no": "Vennligst fullfør dokumentanalysen først."
    }

    go_to_documents_button = {
        "en": "Go to Documents Section",
        "no": "Gå til dokumentseksjonen"
    }

    select_slides_subheader = {
        "en": "Select Slides to Include",
        "no": "Velg lysbilder som skal inkluderes"
    }

    required_slides_header = {
        "en": "Required Slides",
        "no": "Obligatoriske lysbilder"
    }

    optional_slides_header = {
        "en": "Optional Slides",
        "no": "Valgfrie lysbilder"
    }

    confirm_selection_button = {
        "en": "Confirm Slide Selection",
        "no": "Bekreft lysbildevalg"
    }

    modify_selection_button = {
        "en": "Modify Slide Selection",
        "no": "Endre lysbildevalg"
    }

    go_to_preview_button = {
        "en": "Go to Preview",
        "no": "Gå til forhåndsvisning"
    }

    st.header(header_text[current_language])

    if st.checkbox(debug_info_text[current_language]):
        st.write("Session State:", {
            k: v for k, v in st.session_state.items()
            if k not in ['openai_client', 'vector_store']
        })
        st.write("Current Phase:", st.session_state.project_state.current_phase)
        st.write("Slides Present:", bool(st.session_state.project_state.slides))

    if not st.session_state.upload_state.get('processing_complete', False):
        st.info(document_analysis_prompt[current_language])
        if st.button(go_to_documents_button[current_language]):
            st.session_state.active_tab = "Documents"
            st.rerun()
        return

    if 'selected_slides' not in st.session_state:
        st.subheader(select_slides_subheader[current_language])

        st.markdown(f"#### {required_slides_header[current_language]}")
        required_slides_english = {
            "title": "Title Slide",
            "introduction": "Introduction",
            "problem": "Problem Statement",
            "solution": "Solution",
            "market": "Market Opportunity",
            "ask": "Ask",
        }

        required_slides_norwegian = {
            "title": "Tittelslide",
            "introduction": "Introduksjon",
            "problem": "Problemstilling",
            "solution": "Løsning",
            "market": "Markedmuligheter",
            "ask": "Forespørsel",
        }

        # Set the slide names based on the selected language
        required_slides = required_slides_english if current_language == "en" else required_slides_norwegian

        for slide_type, slide_name in required_slides.items():
            st.checkbox(slide_name, value=True, disabled=True, key=f"req_{slide_type}")

        st.markdown(f"#### {optional_slides_header[current_language]}")
        optional_slides_english = {
            "team": "Meet the Team",
            "experience": "Our Experience with the Problem",
            "revenue": "Revenue Model",
            "go_to_market": "Go-To-Market Strategy",
            "demo": "Demo",
            "technology": "Technology",
            "pipeline": "Product Development Pipeline",
            "expansion": "Product Expansion",
            "uniqueness": "Uniqueness & Protectability",
            "competition": "Competitive Landscape",
            "traction": "Traction & Milestones",
            "financials": "Financial Overview",
            "use_of_funds": "Use of Funds"
        }

        optional_slides_norwegian = {
            "team": "Møt Teamet",
            "experience": "Vår Erfaring med Problemet",
            "revenue": "Inntektsmodell",
            "go_to_market": "Gå-til-marked Strategi",
            "demo": "Demo",
            "technology": "Teknologi",
            "pipeline": "Produktutviklingsplan",
            "expansion": "Produktutvidelse",
            "uniqueness": "Unikhet og Beskyttelse",
            "competition": "Konkurranselandskap",
            "traction": "Fremdrift og Milepæler",
            "financials": "Finansiell Oversikt",
            "use_of_funds": "Bruk av Midler"
        }

        # Set the slide names based on the selected language
        optional_slides = optional_slides_english if current_language == "en" else optional_slides_norwegian

        selected_optional = {}

        try:
            # Create thread if needed
            if not st.session_state.get('thread_id'):
                thread = st.session_state.openai_client.beta.threads.create()
                st.session_state.thread_id = thread.id

            # Get documents
            docs = st.session_state.vector_store.get_documents(st.session_state.current_project_id)
            if not docs:
                st.warning("No documents found. Please upload documents first.")
                return

            doc_content = "\n\n".join([doc['content'] for doc in docs if 'content' in doc])

            # Generate slides one by one
            progress_bar = st.progress(0)
            slide_containers = {}

            selected_slide_types = {
                k: v for k, v in (
                    SLIDE_TYPES_NORWEGIAN if st.session_state.current_language == 'no' else SLIDE_TYPES_ENGLISH).items()
                if k in st.session_state.selected_slides and st.session_state.selected_slides[k]
            }

            for slide_type, slide_config in selected_slide_types.items():
                st.subheader(f"{slide_config['name']}")
                slide_containers[slide_type] = st.empty()  # Create placeholder for each slide

            for idx, (slide_type, slide_config) in enumerate(selected_slide_types.items()):
                progress_bar.progress((idx / len(selected_slide_types)))

                # Update status in the slide's container
                slide_containers[slide_type].info(f"Generating {slide_config['name']}...")

                # Define the content for each language
                message_content_english = f"""
                Create a **{slide_config['name']}** slide for a pitch deck using the provided company documents and the following detailed instructions.

                --- 

                ### Slide Objective
                Summarize the **{slide_config['name']}** slide in clear, concise bullet points that are ready for presentation. Focus on informative language, directly addressing the company's context and goals without introductory phrases.

                ### Content Guidelines:
                * Use bullet points to clearly present key information.
                * Aim for precision and relevance to the company's objectives.
                * Include a minimum of three bullet points.

                --- 

                ### Documented Content:
                {doc_content}

                ### Required Elements:
                * {', '.join(slide_config['required_elements'])}

                ### Tone and Style:
                * Formal and professional.
                * Engaging, easy to understand, and well-aligned with company goals.

                --- 

                ### Prompt for Content Creation:
                {slide_config['prompt']}

                --- 

                Directly output the slide content below without additional instructions.
                """

                message_content_norwegian = f"""
                Svar på norsk. Svar kun med punktlister, og unngå introduksjonstekster og forklaringer.

                Lag en **{slide_config['name']}** for en presentasjon med utgangspunkt i selskapets dokumenter og følgende detaljerte instruksjoner.

                ### Mål for lysbilde
                Gi kun klare, konsise punkter for presentasjon. Unngå introduksjonsfraser eller kommentarer.

                ### Innholdskrav:
                * Bruk punktlister for å presentere nøkkelinformasjon.
                * Fokuser på presisjon og relevans for selskapets mål.
                * Hvert punkt skal være under 13 ord.
                * Inkluder minst tre punkter.

                ### Dokumentert innhold:
                {doc_content}

                ### Nødvendige elementer:
                * {', '.join(slide_config['required_elements'])}

                ### Tone og stil:
                * Formelt og profesjonelt.
                * Engasjerende og lett å forstå.

                ### Prompt for innhold:
                {slide_config['prompt']}
                """

                # Select the appropriate message content based on the current language
                message_content = message_content_english if current_language == "en" else message_content_norwegian

                # Send the message content
                st.session_state.openai_client.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=message_content
                )

                run = st.session_state.openai_client.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id="asst_uCXB3ZuddxaZZeEqPh8LZ5Zf"
                )

                while run.status in ["queued", "in_progress"]:
                    slide_containers[slide_type].info(f"Generating {slide_config['name']}... Status: {run.status}")
                    time.sleep(1)
                    run = st.session_state.openai_client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )

                if run.status == "completed":
                    messages = st.session_state.openai_client.beta.threads.messages.list(
                        thread_id=st.session_state.thread_id
                    )

                    response = messages.data[0].content[0].text.value

                    cleaned_response = clean_slide_content(response)

                    if 'raw_responses' not in st.session_state:
                        st.session_state.raw_responses = {}
                    st.session_state.raw_responses[slide_type] = cleaned_response

                    # Show the raw response
                    slide_containers[slide_type].markdown(f"""
                    `
                    {cleaned_response}
                    """)

                    # Parse and save in background
                    slide_content = parse_slide_response(cleaned_response, slide_type)
                    success = st.session_state.project_state.save_slide(slide_type, slide_content)

                    if not success:
                        st.error(f"Failed to save {slide_config['name']}")
                        return
                else:
                    slide_containers[slide_type].error(f"Failed to generate {slide_config['name']}")
                    return

            progress_bar.progress(1.0)
            st.success("✨ All slides generated successfully!")

        except Exception as e:
            st.error(f"Error generating slides: {str(e)}")



import re

def clean_slide_content(response: str) -> str:
    # Remove text starting with '【' and everything after it on the same line

    # Remove any inline formatting indicators like triple backticks or stars around the text
    cleaned_text = re.sub(r"(```|\*\*|\*)", "", response)

    # Trim whitespace for final output and remove empty lines
    cleaned_text = re.sub(r"\n\s*\n", "\n", cleaned_text).strip()

    cleaned_text = re.sub(r"【.*", "", cleaned_text)

    return cleaned_text


if __name__ == "__main__":
    main()
