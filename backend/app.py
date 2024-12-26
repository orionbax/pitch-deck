import logging
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, disconnect
from project_state import ProjectState
from vector_store import VectorStore
from openai import OpenAI
from dotenv import load_dotenv
import os
from pprint import pprint
from messages import SLIDE_TYPES_ENGLISH, SLIDE_TYPES_NORWEGIAN
load_dotenv()
import time

def format_slide_content(slide_config, doc_content):
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
    return message_content_english

def list_assistants(model=None):
    """
    Lists available assistants, optionally filtered by model.
    
    Args:
        model (str, optional): Filter assistants by model name (e.g. "gpt-4", "gpt-3.5-turbo")
    
    Returns:
        list: List of assistant objects matching the criteria
    """
    try:
        assistants = model.beta.assistants.list()
        for asst in assistants.data:
            print(asst.id)
        #     model.beta.assistants.delete(asst.id)
        data = assistants.data
        # model.beta.assistants.delete()
        
        if model:
            # return []
            return [asst for asst in data]# if asst.model == model]
        return data
    except Exception as e:
        logging.error(f"Error listing assistants: {str(e)}")
        return []


class SocketApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'your_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.register_events()
        self.name = "SocketApp"
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # self.asst = self.client.beta.assistants.create(model="gpt-4o-mini", 
        #                                                name="Pitch Deck Assistant", 
        #     instructions="""You are a pitch deck assistant that creates pitch decks for startups. 
        #                     You are given a company document and you create a pitch deck for the company.""")
        # print(self.asst)
        self.assistant_id = "asst_8MAGpmKmGYPgNRMJgX8M6AoC"#"asst_JG70uto633EsWEMYQvBB0aNU"
        # print(f'self.asst: {self.assistant_id}')
        # pprint(list_assistants(self.client))


        self.thread_id = None
        logging.basicConfig(level=logging.INFO)

    def initialize(self):
        # self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.thread_id = None

    def register_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            logging.info("Connecting...")
            logging.info(f'Client connected: {request.sid}')
            username = session.get('username', None)
            if not username:
                logging.info("Client has no username")
                self.socketio.emit('require_auth')
                # return ## REMEMBER TO RE-ENABLE THIS
            session['user'] = {}
            user = session['user']
            user['project_id'] = username or "Athem"
            user['vector_store'] = VectorStore(api_key=os.getenv('PINECONE_API_KEY'))
            user['project_state'] = ProjectState(project_id=user['project_id'], 
                                                 vector_store=user['vector_store'], 
                                                 user=user, client=self.client)
            user['project_state'].load_state()
            if user.get('last_saved_state'):
                lsat_saved = user["last_saved_state"]
                print(f'state: {lsat_saved}')
            else:
                print("No state data found")
            user['current_language'] = 'en'
            if not user.get('client'):
                if not user.get('thread_id'):
                    user['thread_id'] = self.client.beta.threads.create().id

            logging.info(f'{user}, app name: {self.name}')

        @self.socketio.on('generate_slide')
        def generate_slide(slide_type):
            user = session.get('user', {})
            doc_content = user.get('doc_content', '')
            with open('company-detailed-document.txt', 'r') as f:
                doc_content = f.read()
            
            if not doc_content:
                logging.error("Document content is missing.")
                return
            
            slide_type = {
                'name': 'Overview',
                'required_elements': [
                    'Company Name',
                    'Industry',
                    'Mission Statement',
                    'Overview'
                ],
                'prompt': 'Create a concise overview slide text that includes the company name, industry, mission statement and a brief overview. Format it in a clear, presentation-friendly way.'
            }
            
            logging.info(f"Generating slide for type: {slide_type} with doc_content: {doc_content}")

            # Ensure format_slide_content returns a valid string
            slide_content = format_slide_content(slide_type, doc_content)
            if not slide_content:
                logging.error("Formatted slide content is empty or invalid.")
                return

            if not user.get('thread_id'):
                user['thread_id'] = self.client.beta.threads.create().id
            thread_id = user['thread_id']

          
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id,
                # assistant_id='asst_uCXB3ZuddxaZZeEqPh8LZ5Zf',
                additional_instructions=doc_content
            )
            print('finished..')
            print(run.status)

            while run.status in ["queued", "in_progress"]:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                print(run.status)

            if run.status == "completed":
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id,
                )
                # pprint(messages)
                pprint(messages.data)
                response = messages.data[0].content[0].text.value
                print(f"response: {response}")
                # print(len(response))
                # self.socketio.emit('slide_generated', f"Slide {slide_type['name']} generated")

        @self.socketio.on('message')
        def handle_message(msg):
            username = session.get('username', None)
            print(msg)
            if username:
                user_id = request.sid
                logging.info(f'Message from {username} ({user_id}): {msg}')
                self.socketio.emit('response', f'Hello {username}, {msg}')
                return
            self.socketio.emit('require_auth')

        @self.socketio.on('disconnect')
        def handle_disconnect():
            user_id = request.sid
            authenticated = session.get('authenticated', False)
            username = session.get('username', 'Anonymous')
            logging.info(f'Client disconnected: {username} ({user_id}) (Authenticated: {authenticated})')

        @self.socketio.on('get_slide_options')
        def get_slide_options():
            request_data = request.get_json()
            language = request_data.get('language', 'en')

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

            if language == "en":
                slide_options = {'required': required_slides_english, 'optional': optional_slides_english}
            else:
                slide_options = {'required': required_slides_norwegian, 'optional': optional_slides_norwegian}

            logging.info("Getting slide options")
            self.socketio.emit('slide_options', slide_options)

        @self.socketio.on('generate_slide2')
        def get_slide_types2(msg):
            language = 'en'
            selected_slides = ["title", "introduction"]#, "problem", "solution", "market", "ask"]
            
            slide_config = SLIDE_TYPES_ENGLISH if language == "en" else SLIDE_TYPES_NORWEGIAN
            user = session.get('user', {})
            
            with open('company-detailed-document.txt', 'r') as f:
                doc_content = f.read()

            selected_slide_configs = {k: v for k, v in slide_config.items() if k in selected_slides}
            
            # if not user.get('thread_id'):
            #     thread = self.client.beta.threads.create()
            #     user['thread_id'] = thread.id

            for slide_type, config in selected_slide_configs.items():
                message_content = format_slide_content(config, doc_content)
                
                self.client.beta.threads.messages.create(
                    thread_id=user['thread_id'],
                    role="user", 
                    content=message_content
                )

                run = self.client.beta.threads.runs.create(
                    thread_id=user['thread_id'],
                    assistant_id=self.assistant_id
                )

                while run.status in ["queued", "in_progress"]:
                    time.sleep(1)
                    run = self.client.beta.threads.runs.retrieve(
                        thread_id=user['thread_id'],
                        run_id=run.id
                    )

                if run.status == "completed":
                    messages = self.client.beta.threads.messages.list(
                        thread_id=user['thread_id']
                    )
                    
                    response = messages.data[0].content[0].text.value
                    cleaned_response = response
                    
                    if 'raw_responses' not in user:
                        user['raw_responses'] = {}
                    print(f'config: {config["name"]}')
                    user['raw_responses'][config['name']] = cleaned_response
                    print(f'slide_content: {cleaned_response}')
                    user['vector_store'].store_slide(user['project_id'], config['name'], cleaned_response, language)
                    print(f'set {config["name"]} to vector store')
                    print(f'from slide: ', user['vector_store'].get_latest_slides(user['project_id'], language))
                    self.socketio.emit('slide_content', {
                        'content': cleaned_response,
                        'slide_name': config['name']
                    })
                    
                    success = True  # Replace with actual save logic
                    if not success:
                        self.socketio.emit('error', {'message': f"Failed to save {config['name']}"})
                        return
                        
                    self.socketio.emit('progress', {'progress': 1.0})
                    self.socketio.emit('response', {'message': "✨ Slide generated successfully!"})
                else:
                    self.socketio.emit('error', {'message': "Failed to generate slide content"})
                    return
    def run(self, host='0.0.0.0', port=5000):
        logging.info(f"Server is running on http://{host}:{port}")
        self.socketio.run(self.app, host=host, port=port)




if __name__ == '__main__':
    logging.info("Initializing SocketApp")
    socket_app = SocketApp()
    logging.info("Running SocketApp")
    socket_app.run()



