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
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Flask
app = Flask(__name__)
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
app.secret_key = '1234567890'
# Enable CORS for all routes with credentials
CORS(app, supports_credentials=True)

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

def log_session_info(endpoint_name):
    logging.info(f"Session data at {endpoint_name}: {session}")

@app.route('/create_project', methods=['POST'])
def create_project():
    log_session_info('create_project')
    project_id = request.json.get('project_id')
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400

    # Initialize session if not already done
    if 'user' not in session or session['user'].get('project_id') != project_id:
        session['user'] = {}
        user = session['user']
        user['project_id'] = project_id
        user['documents'] = []  # Initialize documents as a list
        user['state'] = {
            'project_id': project_id,
            'current_phase': 0,
            'current_language': 'en',
            'slides': {},
            'html_preview': False,
            'pdf_generated': False,
            'timestamp': datetime.now().isoformat(),
        }
        user['thread_id'] = OpenAI(api_key=os.getenv('OPENAI_API_KEY')).beta.threads.create().id
        logging.info(f"Project created: {user}")

    logging.info(f"Session data after creation: {session['user']}")
    return jsonify(session['user']['state'])

@app.route('/upload_documents', methods=['POST'])
def upload_documents():
    log_session_info('upload_documents')
    if 'user' not in session:
        return jsonify({'error': 'No active project session'}), 400

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

            processed_documents.append({
                'filename': filename,
                'content': content
            })
        except Exception as e:
            logging.error(f"Error processing file {filename}: {str(e)}")
            continue

    if processed_documents:
        # Update the documents in the session
        session['user']['documents'].extend(processed_documents)
        logging.info(f"Updated user documents: {session['user']['documents']}")
        return jsonify({'status': 'success', 'message': f'{len(processed_documents)} documents processed'})
    else:
        return jsonify({'error': 'No valid documents were processed'}), 400

@app.route('/generate_slides', methods=['POST'])
def generate_slides():
    log_session_info('generate_slides')
    if 'user' not in session:
        return jsonify({'error': 'No active project session'}), 400

    slides = request.json.get('slides', [])
    user = session['user']
    logging.info(f"User in generate_slides: {user}")
    documents = user.get('documents', [])
    thread_id = user.get('thread_id')
    assistant_id = "asst_8MAGpmKmGYPgNRMJgX8M6AoC"

    if not documents:
        return jsonify({'error': "No documents provided"}), 400

    # Start the slide processing in a separate thread
    threading.Thread(target=process_slides, args=(documents, thread_id, slides, assistant_id)).start()
    return jsonify({'status': 'processing'})

def process_slides(documents, thread_id, slides, assistant_id):
    try:
        logging.info("Starting slide processing")
        language = 'en'
        slide_config = SLIDE_TYPES_ENGLISH if language == "en" else SLIDE_TYPES_NORWEGIAN
        selected_slides = {k: v for k, v in slide_config.items() if k in slides}

        doc_content = ''.join([document['content'] for document in documents])
        required_slides = {k: v for k, v in slide_config.items() if k in required_slides_english}
        selected_slide_configs = {**required_slides, **{k: v for k, v in slide_config.items() if k in selected_slides}}

        for slide_type, config in selected_slide_configs.items():
            logging.info(f"Processing slide: {slide_type}")
            message_content = format_slide_content(config, doc_content)
            
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
                    'status': 'progress'
                }
                logging.info(f"Slide content: {slide_content}")

                # Store or process slide content as needed
            else:
                logging.error("Failed to generate slide content")
                return
        logging.info("Slide processing completed")
    except Exception as e:
        logging.error(f"Error processing slides: {str(e)}")

def format_slide_content(slide_config, doc_content):
    return f"""
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

if __name__ == '__main__':
    logging.info("Starting Flask app")
    app.run(host='0.0.0.0', port=5000, debug=True)



