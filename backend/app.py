import logging
import os
from datetime import datetime
# from pprint import pprint
from flask import Flask, session, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from messages import SLIDE_TYPES_ENGLISH, SLIDE_TYPES_NORWEGIAN

import PyPDF2
from docx import Document
import time
from database import DatabaseManager
from s3_manager import S3Manager
import secrets  # Add this import for token generation
# from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth

import tempfile


load_dotenv()
assistant_id = os.getenv('ASSISTANT_ID')
# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable logging
logging.basicConfig(level=logging.CRITICAL + 1)

# Initialize Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
# Enable CORS for all routes with credentials
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})


prompt = """
You are an expert business development professional specializing in crafting the written content for pitch decks tailored to start-ups. Your role focuses exclusively on the verbal and written components within the slides—not the visual design. You’ve recently joined a new business consultancy, where your main responsibility is developing compelling, investor-focused content for pitch decks.

To align with the specific style and standards of your new company, your primary task is to follow the guidelines outlined in The Ultimate Guide to Creating Pitch Decks.md, available within your files in knowledge. This guide contains detailed instructions on  tone, and content style, serving as the foundational reference for your work.


Writing Style:
	•	Concise and Direct: Use bullet points to convey information clearly and efficiently.
	•	Professional yet Approachable: Combine professionalism with an accessible tone.
	•	Action-Oriented and Confident: Maintain a confident, forward-thinking tone that positions the company as an innovative problem-solver.
	•	Strategically Structured: Anticipate and address potential questions or objections. Use quantitative data to support claims where relevant.
	•	Relatable with Controlled Jargon: Include personal elements to build trust while using industry jargon sparingly, ensuring accessibility to a broad audience.
	•	Value-Focused: Tie each feature to specific benefits, emphasizing the value proposition for both customers and investors.
	•	Future-Oriented: Highlight scalability and long-term potential, building towards a clear call-to-action for investment.
	•	Introduction Slide: Limit to a single, well-crafted paragraph.

Tone:
	•	Innovative and Solution-Oriented: Present the company as a forward-thinking leader ready to tackle industry challenges.
	•	Optimistic yet Grounded: Convey enthusiasm for the company’s vision and potential while demonstrating a realistic understanding of market dynamics.
	•	Investor-Centric: Directly address investor concerns, maintaining a focus on tangible outcomes and ROI.
	•	Engaging and Collaborative: Foster a sense of openness and partnership, while asserting thought leadership.
	•	Trust-Building: Use personal elements strategically to build rapport without compromising professionalism, inspiring confidence in the company’s capabilities and vision.

Additional Rules:
	1.	Text-Heavy Content: Only the Introduction slide may contain text blocks. All other slides should use concise, meaningful bullet points.
	•	Limit each bullet point to 13 words or fewer to maintain brevity and clarity.
	•	Avoid complex sentence structures; prioritize simplicity and directness.
	2.	Visuals vs. Text (When Beneficial): For each slide, evaluate if visuals would enhance information presentation (e.g., flowcharts, user journeys, comparisons). Suggest replacing or supplementing text with visuals only when they add value to understanding the content.
	3.	Slide Titles: Use simple, industry-standard terminology for slide titles. Ensure titles are clear, context-appropriate, and avoid unnecessary complexity.
	4.	Formatting: Use only bullet-point formatting, without bolding or highlighting.
	•	Do not start bullet points with an emboldened word or phrase.
	•	Format bullet points as follows:
	•	Bullet point text.
	•	Bullet point text.
	•	Example: Instead of writing, “AI-Powered Personalization: Custom personas simulate expert roles, providing industry-specific feedback,” write, “Custom personas simulate expert roles, providing industry-specific feedback through AI-powered personalization.”

Reference Document:
The Ultimate Guide to Creating Pitch Decks.md – This document contains the complete set of instructions for structuring, styling, and phrasing pitch deck content and should be consulted from your files in knowledge
"""

# prompt = """
# You are a skilled business development professional specializing in creating compelling written content for start-up pitch decks. Your expertise lies in crafting the verbal and textual components of slides, not the visual design. Recently, you joined a new business consultancy, where your primary responsibility is developing investor-focused pitch deck content that aligns with the company's specific style and standards.

# Your primary guide for this task is The Ultimate Guide to Creating Pitch Decks.md, provided for you. This document provides detailed instructions on tone, content structure, and style, and serves as your foundational reference. Your work must closely adhere to the principles outlined in this guide.
# Writing Style:

# Your writing should reflect the following characteristics:

#     Concise and Direct:
#     Convey information clearly and efficiently using bullet points to avoid unnecessary verbosity.
#     Professional yet Approachable:
#     Strike a balance between professionalism and accessibility to create a tone that feels welcoming without being overly casual.
#     Action-Oriented and Confident:
#     Use confident, forward-thinking language that positions the company as an innovative problem-solver.
#     Strategically Structured:
#     Anticipate potential investor questions or objections and address them proactively. Where relevant, use quantitative data to substantiate claims.
#     Relatable with Controlled Jargon:
#     Include relatable elements to build trust while limiting the use of technical or industry-specific jargon to ensure broad accessibility.
#     Value-Focused:
#     Highlight the value proposition of each feature, clearly tying it to specific benefits for customers and investors.
#     Future-Oriented:
#     Emphasize scalability and long-term potential, leading to a strong, clear call-to-action for investment.
#     Introduction Slide:
#     Craft a single, well-written paragraph for the introduction slide that effectively summarizes the pitch deck's core message.

# Tone:

# Adopt a tone that conveys the following attributes:

#     Innovative and Solution-Oriented:
#     Present the company as a leader with the vision and ability to tackle key industry challenges.
#     Optimistic yet Grounded:
#     Balance enthusiasm for the company’s vision with a realistic understanding of market dynamics.
#     Investor-Centric:
#     Keep the focus on tangible outcomes and return on investment (ROI) to address investor concerns directly.
#     Engaging and Collaborative:
#     Create a sense of openness and partnership, while maintaining thought leadership.
#     Trust-Building:
#     Use personal, relatable elements to inspire confidence without compromising professionalism.

# Additional Rules:

# To ensure clarity and effectiveness, adhere to the following guidelines:

#     Text-Heavy Content:
#         Only the introduction slide may include text blocks; all other slides should rely on concise bullet points.
#         Limit each bullet point to 13 words or fewer for brevity and impact.
#         Use simple sentence structures, prioritizing directness and clarity.

#     Visuals vs. Text:
#         Evaluate whether visuals (e.g., flowcharts, user journeys, comparisons) would enhance understanding.
#         Suggest replacing or supplementing text with visuals only when they add clear value.

#     Slide Titles:
#         Use industry-standard, straightforward terminology for slide titles.
#         Avoid unnecessary complexity, ensuring each title is clear and context-appropriate.

#     Formatting:
#         Employ bullet-point formatting exclusively; avoid bolding or highlighting.
#         Do not begin bullet points with bold or emphasized words.
#         Example: Instead of writing, “AI-Powered Personalization: Custom personas simulate expert roles, providing industry-specific feedback,” write:
#             “Custom personas simulate expert roles, providing industry-specific feedback through AI-powered personalization.”

# Reference Document:

# The Ultimate Guide to Creating Pitch Decks.md – This document provides a comprehensive set of instructions on structuring, styling, and phrasing pitch deck content. Always refer to this guide for consistency and alignment with company standards.

# """
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

def generate_secure_token():
    """Generate a secure token for project authentication"""
    return secrets.token_urlsafe(32)

def verify_token(f):
    """Decorator to verify token for protected routes"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        # Remove 'Bearer ' prefix if present
        token = token.replace('Bearer ', '')
        
        # Verify token exists in database
        project = db_manager.get_project_by_token(token)
        if not project:
            return jsonify({'error': 'Invalid token'}), 401
            
        # Add project info to request context
        request.project = project
        return f(*args, **kwargs)
    return decorated_function

@app.route('/delete_project', methods=['POST'])
@verify_token
def delete_project():
    project = request.project
    project_id = project['project_id']
    
    logging.info(f"Attempting to delete project: {project_id}")
    
    try:
        # Delete project and all associated data
        success = db_manager.delete_project(project_id)
        
        # Wait a moment to ensure deletion is processed
        time.sleep(0.5)
        
        # Verify deletion
        verification = db_manager.get_project(project_id)
        if verification:
            logging.error(f"Project still exists after deletion: {project_id}")
            # Try one more time
            db_manager.delete_project(project_id)
            time.sleep(0.5)
            
            # Final verification
            final_check = db_manager.get_project(project_id)
            if final_check:
                return jsonify({'error': 'Project deletion failed - project still exists'}), 500
            
        if success:
            # Also delete associated documents from S3
            try:
                s3_manager.delete_project_documents(project_id)
            except Exception as s3_error:
                logging.error(f"Error deleting S3 documents: {str(s3_error)}")
                # Continue even if S3 deletion fails
                
            logging.info(f"Successfully deleted project: {project_id}")
            return jsonify({
                'status': 'success', 
                'message': 'Project deleted',
                'project_id': project_id,
                'verified': True
            })
        else:
            logging.error(f"Database deletion failed for project: {project_id}")
            return jsonify({'error': 'Failed to delete project from database'}), 500
            
    except Exception as e:
        logging.error(f"Error deleting project: {str(e)}")
        return jsonify({'error': f'Error deleting project: {str(e)}'}), 500

@app.route('/create_project', methods=['POST'])
def create_project():
    project_id = request.json.get('project_id')
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400

    # Check if project already exists
    existing_project = db_manager.get_project(project_id)
    if existing_project:
        # Check if project has a token, if not generate one
        if 'token' not in existing_project:
            token = generate_secure_token()
            db_manager.update_project_token(project_id, token)
            existing_project['token'] = token
        
        return jsonify({
            'token': existing_project['token'],
            'state': existing_project.get('state', {'current_language': 'en', 'slides': {}}),
            'message': 'Using existing project',
            'documents': True if existing_project.get('documents', False) else False
        })

    # Generate secure token for new project
    token = generate_secure_token()
    
    # Create new thread
    thread_id = OpenAI(api_key=os.getenv('OPENAI_API_KEY')).beta.threads.create().id
    
    # Create project in database with token
    try:
        project = db_manager.create_project(project_id, thread_id, token)
        return jsonify({
            'token': token,
            'state': project['state'],
            'message': 'New project created'
        })
    except Exception as e:
        logging.error(f"Error creating project: {str(e)}")
        return jsonify({'error': 'Failed to create project'}), 500

@app.route('/upload_documents', methods=['POST'])
@verify_token
def upload_documents():
    project = request.project
    project_id = project['project_id']
    
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
@verify_token
def set_language():
    project = request.project
    project_id = project['project_id']
    language = request.json.get('language')
    
    if language in ['en', 'no']:
        try:
            # Update language in database
            success = db_manager.update_project_language(project_id, language)
            if success:
                # Update the project state in request context
                project['state']['current_language'] = language
                return jsonify({
                    'status': 'success', 
                    'message': f'Language set to {language}',
                    'state': project['state']
                })
            else:
                return jsonify({'error': 'Failed to update language'}), 500
        except Exception as e:
            logging.error(f"Error setting language: {str(e)}")
            return jsonify({'error': f'Error setting language: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Invalid language'}), 400

@app.route('/generate_slides', methods=['POST'])
@verify_token
def generate_slides():
    project = request.project
    project_id = project['project_id']
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
        
        # Get project from request context
        project = request.project
        language = project['state'].get('current_language', 'en')
        
        slide_config = SLIDE_TYPES_ENGLISH if language == "en" else SLIDE_TYPES_NORWEGIAN
        slide_name = slide.lower().replace(' ', '_')
        print('the slide name is: ', slide_name)
        config = slide_config.get(slide_name, None)

        if not config:
            logging.error(f"Slide configuration not found for: {slide}")
            return None

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
@verify_token
def edit_slide():
    project = request.project
    slide = request.json.get('slide')
    edit_request = request.json.get('edit_request')
    
    # Get current slide content from database
    current_content = db_manager.get_slide_content(project['project_id'], slide)
    if not current_content:
        return jsonify({'error': 'Slide not found'}), 404

    logging.info(f"Received edit request: {edit_request} for slide: {slide}")
    message_content = get_edit_prompt(project['state']['current_language'], edit_request, current_content)
    logging.info(f"Generated message content: {message_content}")
    thread_id = project['thread_id']

    try:
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
            
            # Update slide content in database
            db_manager.update_slide_content(project['project_id'], slide, cleaned_response)
            
            logging.info(f"Slide content updated: {slide_content}")
            return jsonify({'status': 'completed', 'content': slide_content})
        else:
            logging.error("Failed to generate slide content")
            return jsonify({'error': 'Failed to generate slide content'}), 500

    except Exception as e:
        logging.error(f"Error editing slide: {str(e)}")
        return jsonify({'error': f'Error editing slide: {str(e)}'}), 500

def get_edit_prompt(language, edit_request, current_content):
    """Generate edit prompt based on language"""
    if language == "no":
        # Norwegian prompt
        return f"""Vennligst oppdater denne lysbilden basert på følgende forespørsel:

        Nåværende Innhold:
        {current_content}

        Redigeringsforespørsel:
        {edit_request}

        Vennligst behold samme format og struktur, men innlem de ønskede endringene."""
    else:
        # English prompt (default)
        return f"""Please update this slide based on the following request:

        Current Content:
        {current_content}

        Edit Request:
        {edit_request}

        Please maintain the same format and structure, but incorporate the requested changes."""

def format_slide_content(config, doc_content):
    """Format slide content based on configuration"""
    message_content_english = f"""
        Create a **{config['name']}** slide for a pitch deck using the provided company documents and the following detailed instructions.

        --- 

        ### Slide Objective
        Summarize the **{config['name']}** slide in clear, concise bullet points that are ready for presentation. Focus on informative language, directly addressing the company's context and goals without introductory phrases.

        ### Content Guidelines:
        * Use bullet points to clearly present key information.
        * Aim for precision and relevance to the company's objectives.
        * Include a minimum of three bullet points.

        --- 

        ### Documented Content:
        {doc_content}

        ### Required Elements:
        * {', '.join(config['required_elements'])}

        ### Tone and Style:
        * Formal and professional.
        * Engaging, easy to understand, and well-aligned with company goals.

        --- 

        ### Prompt for Content Creation:
        {config['prompt']}

        --- 

        Directly output the slide content below without additional instructions.
    """

    message_content_norwegian = f"""
        Svar på norsk. Svar kun med punktlister, og unngå introduksjonstekster og forklaringer.

        Lag en **{config['name']}** for en presentasjon med utgangspunkt i selskapets dokumenter og følgende detaljerte instruksjoner.

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
        * {', '.join(config['required_elements'])}

        ### Tone og stil:
        * Formelt og profesjonelt.
        * Engasjerende og lett å forstå.

        ### Prompt for innhold:
        {config['prompt']}
        """

    # Get project from request context
    project = request.project
    language = project['state'].get('current_language', 'en')
    
    return message_content_english if language == "en" else message_content_norwegian

@app.route('/test_cors', methods=['GET'])
def test_cors():
    return jsonify({'message': 'CORS is working!'})


@app.route('/download_pdf', methods=['POST'])
@verify_token
def download_pdf():
    logging.info("Downloading PDF")
    project = request.project
    project_id = project['project_id']
    project_data = db_manager.get_project(project_id)
    
    original_slides = project_data['state']['slides']#[]
    slides = sort_slides(original_slides, 
                         project_data['state']['current_language'])

    if not slides:
        return jsonify({'error': 'No slides available for this project'}), 404
    
    selected_language = project_data['state']['current_language']
   

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        c = canvas.Canvas(temp_pdf.name, pagesize=A4)
        width, height = A4
        margin = 60  # Increased margin for better readability
        y_position_start = height - margin

        first_page = True  # Track if it's the first page
        bullet_symbol = "•" if selected_language == "en" else "-"  # Choose bullet symbol based on language
        # for slide_name in
        # for slide_name, slide_content in slides.items():
        for slide_name in slides:
            # print('the slide_name is: ', slide_name)
            # slide_name = original_slides[]
            slide_content = original_slides[slide_name]
            if not first_page:
                c.showPage()  # Start a new page for each slide except the first
            else:
                first_page = False  # Skip creating a new page for the first slide

            y_position = y_position_start

            # Draw slide title
            c.setFont("Helvetica-Bold", 20)
            c.drawString(margin, y_position, slide_name)
            y_position -= 32  # Space after title

            # Determine slide type and format content accordingly
            if slide_name.lower() == 'introduction':
                # Introduction slide with paragraph format
                for line in slide_content.split('\n'):
                    if line.strip():
                        line = line.replace('**', '').strip()
                        if line.startswith('- '):
                            line = line[2:]

                        # Adjust x position and max width for bullet points
                        bullet_indent = margin + 10
                        bullet_width = width - 2 * margin - 20
                        c.setFont("Helvetica", 10)
                        y_position = draw_text_paragraph(
                            c, f"{bullet_symbol} {line}", y_position, margin, width - 2 * margin,
                            font="Helvetica", font_size=10, line_height=14
                        )
            else:
                # Bullet point format for other slides
                for line in slide_content.split('\n'):
                    if line.strip():
                        line = line.replace('**', '').strip()
                        if line.startswith('- '):
                            line = line[2:]

                        # Adjust x position and max width for bullet points
                        bullet_indent = margin + 10
                        bullet_width = width - 2 * margin - 20
                        c.setFont("Helvetica", 10)
                        y_position = draw_text_paragraph(
                            c, f"{bullet_symbol} {line}", y_position, bullet_indent, bullet_width,
                            font="Helvetica", font_size=10, line_height=14
                        )

        c.save()

    return send_file(temp_pdf.name, as_attachment=True, download_name=f"{project_id}_slides.pdf")

from pprint import pprint
def sort_slides(slides, selected_language):    
    selected_slides = SLIDE_TYPES_ENGLISH if selected_language == 'en' else SLIDE_TYPES_NORWEGIAN
    all_slides = [slide_name for slide_name, _ in selected_slides.items()]
    new_slides = []
    # print('the all_slides are: ', end='')
    # pprint( all_slides)
    for slide_name in all_slides:
        for name, content in slides.items():
            if name == slide_name:
                new_slides.append(name)
    # print('The new slides are: ', end='')
    # pprint(new_slides)
    
    return new_slides

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

if __name__ == '__main__':
    logging.info("Starting Flask app")
    app.run(host='0.0.0.0', port=5000, debug=True)