import logging
import os
from datetime import datetime
from flask import Flask, session, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from messages import SLIDE_TYPES_ENGLISH, SLIDE_TYPES_NORWEGIAN
import threading
import io
import PyPDF2
from docx import Document
import time
from database import DatabaseManager
from s3_manager import S3Manager


load_dotenv()
assistant_id = os.getenv('ASSISTANT_ID')
# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable logging
logging.basicConfig(level=logging.CRITICAL + 1)

# Initialize Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Enable CORS for all routes with credentials
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Define slide options
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

required_slides_english = {
    "title": "Title Slide",
    "introduction": "Introduction",
    "problem": "Problem Statement",
    "solution": "Solution",
    "market": "Market Opportunity",
    "ask": "Ask",
}

# Add DatabaseManager initialization
db_manager = DatabaseManager()
s3_manager = S3Manager()

def log_session_info(endpoint_name):
    logging.info(f"Session data at {endpoint_name}: {session}")

@app.route('/delete_project', methods=['POST'])
def delete_project():
    project_id = request.json.get('project_id')
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400
    
    db_manager.delete_project(project_id)
    session.clear()
    session.modified = True
    return jsonify({'status': 'success', 'message': 'Project deleted'})

@app.route('/create_project', methods=['POST'])
def create_project():
    project_id = request.json.get('project_id')
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400

    # Create new thread
    thread_id = OpenAI(api_key=os.getenv('OPENAI_API_KEY')).beta.threads.create().id
    
    # Create project in database
    project = db_manager.create_project(project_id, thread_id)
    
    # Update session
    session['user'] = {
        'project_id': project_id,
        'thread_id': thread_id,
        'state': project['state']
    }
    session.modified = True
    
    return jsonify(project['state'])

@app.route('/upload_documents', methods=['POST'])
def upload_documents():
    if 'user' not in session:
        return jsonify({'error': 'No active project session'}), 400

    project_id = session['user']['project_id']
    
    if 'documents' not in request.files:
        return jsonify({'error': 'No documents provided'}), 400

    files = request.files.getlist('documents')
    processed_documents = []

    for file in files:
        filename = file.filename
        file_ext = filename.split('.')[-1].lower()

        try:
            if file_ext == 'pdf':
                # Read PDF content
                pdf_reader = PyPDF2.PdfReader(file)
                content = ' '.join(page.extract_text() for page in pdf_reader.pages)
            elif file_ext == 'docx':
                # Read DOCX content
                doc = Document(file)
                content = ' '.join(paragraph.text for paragraph in doc.paragraphs)
            elif file_ext == 'txt':
                # Read TXT content
                content = file.read().decode('utf-8')
            else:
                continue

            # Upload to S3
            s3_key = s3_manager.upload_document(project_id, filename, content)
            
            # Store metadata in MongoDB
            document_metadata = {
                'filename': filename,
                'file_type': file_ext,
                's3_key': s3_key,
                'uploaded_at': datetime.now().isoformat()
            }
            
            db_manager.add_document(project_id, document_metadata)
            processed_documents.append(document_metadata)

        except Exception as e:
            logging.error(f"Error processing file {filename}: {str(e)}")
            continue

    if processed_documents:
        return jsonify({'status': 'success', 'message': f'{len(processed_documents)} documents processed'})
    else:
        return jsonify({'error': 'No valid documents were processed'}), 400

@app.route('/set_language', methods=['POST'])
def set_language():
    if 'user' not in session:
        return jsonify({'error': 'No active project session'}), 400
        
    project_id = session['user']['project_id']
    language = request.json.get('language')
    
    if language in ['en', 'no']:
        # Update language in database
        db_manager.update_project_language(project_id, language)
        session['user']['state']['current_language'] = language
        session.modified = True
        return jsonify({'status': 'success', 'message': f'Language set to {language}'})
    else:
        return jsonify({'error': 'Invalid language'}), 400

@app.route('/generate_slides', methods=['POST'])
def generate_slides():
    if 'user' not in session:
        return jsonify({'error': 'No active project session'}), 400

    project_id = session['user']['project_id']
    slide = request.json.get('slide')
    
    # Get project from database
    project = db_manager.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    documents = project.get('documents', [])
    thread_id = project.get('thread_id')

    if not documents:
        return jsonify({'error': "No documents provided"}), 400

    if not slide:
        return jsonify({'error': "No slide specified"}), 400

    slide_content = process_slide(documents, thread_id, slide, assistant_id)
    if slide_content:
        # Store slide content in database
        db_manager.update_slide_content(project_id, slide, slide_content)
        session['user']['state']['slides'][slide] = slide_content
        session.modified = True
        return jsonify({'status': 'completed', 'content': slide_content})
    else:
        return jsonify({'error': 'Failed to generate slide content'}), 500

def process_slide(documents, thread_id, slide, assistant_id):
    try:
        # Get document contents from S3
        doc_contents = []
        for doc in documents:
            content = s3_manager.get_document(doc['s3_key'])
            doc_contents.append(content)

        doc_content = ' '.join(doc_contents)
        logging.info(f"Processing slide: {slide}")
        language = session['user']['state'].get('current_language', 'en')
        # print('language\n', language)
        slide_config = SLIDE_TYPES_ENGLISH if language == "en" else SLIDE_TYPES_NORWEGIAN
        config = slide_config.get(slide)

        if not config:
            logging.error(f"Slide configuration not found for: {slide}")
            return None

        message_content = format_slide_content(config, doc_content)
        # print('message_content\n', message_content)
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user", 
            content=message_content
        )

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        while run.status in ["queued", "in_progress"]:
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

        if run.status == "completed":
            messages = client.beta.threads.messages.list(
                thread_id=thread_id
            )
            
            response = messages.data[0].content[0].text.value
            cleaned_response = response
            
            slide_content = {
                'content': cleaned_response,
                'slide_name': config['name'],
                'status': 'completed'
            }
            logging.info(f"Slide content: {slide_content}")
            return slide_content['content']
        else:
            logging.error("Failed to generate slide content")
            return None
    except Exception as e:
        logging.error(f"Error processing slide: {str(e)}")
        return None

@app.route('/edit_slide', methods=['POST'])
def edit_slide():
    language = session['user']['state'].get('current_language', 'en')
    slide = request.json.get('slide')
    edit_request = request.json.get('edit_request')
    logging.info(f"Received edit request: {edit_request} for slide: {slide}")
    message_content = get_edit_prompt(language, edit_request, slide)
    logging.info(f"Generated message content: {message_content}")
    thread_id = session['user']['thread_id']

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user", 
        content=message_content
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    while run.status in ["queued", "in_progress"]:
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

    if run.status == "completed":
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        
        response = messages.data[0].content[0].text.value
        cleaned_response = response
        
        slide_content = {
            'content': cleaned_response,
            'status': 'completed'
        }
        logging.info(f"Slide content: {slide_content}")
    else:
        logging.error("Failed to generate slide content")

    if slide_content:
        session.modified = True  # Ensure session is marked as modified
        return jsonify({'status': 'completed', 'content': slide_content})
    
    return jsonify({'error': 'Failed to modify slide content'}), 500

def get_edit_prompt(language, edit_request, slide):
    current_content = session['user']['state']['slides'][slide]
    language = session['user']['state'].get('current_language', 'no')

    if language == "no":
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
    return message_content
        


def format_slide_content(slide_config, doc_content):
    # print('\n get language\n', session['user']['state'].get('current_language', None))
    language = session['user']['state'].get('current_language', 'no')
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
    # print('\nlanguage\n', language)
    if language == "en":
        return message_content_english
    else:
        return message_content_norwegian

@app.route('/test_cors', methods=['GET'])
def test_cors():
    return jsonify({'message': 'CORS is working!'})

# @app.before_first_request
# def clear_session_on_startup():
#     session.clear()
#     logging.info("Session cleared on startup")

if __name__ == '__main__':
    logging.info("Starting Flask app")
    app.run(host='0.0.0.0', port=5000, debug=True)



