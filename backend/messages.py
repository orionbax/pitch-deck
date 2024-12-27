from typing import Dict, List, Optional

# English phase names
PHASE_NAMES_ENGLISH = [
    "Phase 0: Document Analysis",
    "Phase 1: Slide Planning",
    "Phase 2: Content Generation",
    "Phase 3: Language Processing",
    "Phase 4: HTML Preview",
    "Phase 5: PDF Generation",
    "Phase 6: Canva Export"
]

# Norwegian phase names
PHASE_NAMES_NORWEGIAN = [
    "Fase 0: Dokumentanalyse",
    "Fase 1: Lysbildeplanlegging",
    "Fase 2: Innholdsgenerering",
    "Fase 3: Språkbehandling",
    "Fase 4: HTML-forhåndsvisning",
    "Fase 5: PDF-generering",
    "Fase 6: Canva-eksport"
]

# English phase configurations
PHASE_CONFIGS_ENGLISH = {
    "Phase 0: Document Analysis": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Analyzes uploaded documents to understand company information",
        "requires_previous": False,
        "output_format": "report"
    },
    "Phase 1: Slide Planning": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Plans slide structure and content distribution",
        "requires_previous": True,
        "output_format": "json"
    },
    "Phase 2: Content Generation": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Generates content for each slide based on analysis",
        "requires_previous": True,
        "output_format": "slides"
    },
    "Phase 3: Language Processing": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Handles translation and language optimization",
        "requires_previous": True,
        "output_format": "slides"
    },
    "Phase 4: HTML Preview": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Generates interactive HTML preview of slides",
        "requires_previous": True,
        "output_format": "html"
    },
    "Phase 5: PDF Generation": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Creates PDF version of the pitch deck",
        "requires_previous": True,
        "output_format": "pdf"
    },
    "Phase 6: Canva Export": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Prepares and exports content to Canva",
        "requires_previous": True,
        "output_format": "canva"
    }
}

# Norwegian phase configurations
PHASE_CONFIGS_NORWEGIAN = {
    "Fase 0: Dokumentanalyse": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Analyserer opplastede dokumenter for å forstå selskapsinformasjon",
        "requires_previous": False,
        "output_format": "report"
    },
    "Fase 1: Lysbildeplanlegging": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Planlegger lysbildestruktur og innholdsdistribusjon",
        "requires_previous": True,
        "output_format": "json"
    },
    "Fase 2: Innholdsgenerering": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Genererer innhold for hvert lysbilde basert på analyse",
        "requires_previous": True,
        "output_format": "slides"
    },
    "Fase 3: Språkbehandling": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Håndterer oversettelse og språkopptimalisering",
        "requires_previous": True,
        "output_format": "slides"
    },
    "Fase 4: HTML-forhåndsvisning": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Genererer interaktiv HTML-forhåndsvisning av lysbilder",
        "requires_previous": True,
        "output_format": "html"
    },
    "Fase 5: PDF-generering": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Oppretter PDF-versjon av presentasjonen",
        "requires_previous": True,
        "output_format": "pdf"
    },
    "Fase 6: Canva-eksport": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Forbereder og eksporterer innhold til Canva",
        "requires_previous": True,
        "output_format": "canva"
    }
}

# English slide types
SLIDE_TYPES_ENGLISH = {
    "title": {
        "name": "Title Slide",
        "prompt": "Generate a title slide with the company's name, tagline, and a cohesive visual theme that captures the company's essence.",
        "required_elements": ["company_name", "tagline"],
    },
    "introduction": {
        "name": "Introduction",
        "prompt": "Provide a brief, engaging summary of the company, focusing on a hook that captures interest and explains the company's core value proposition.",
        "required_elements": ["summary", "hook"],
    },
    # Add other slide types as needed
}

SLIDE_TYPES_NORWEGIAN = {
    "title": {
        "name": "Tittelside",
        "prompt": "Generer en tittelside med selskapets navn, slagord og et sammenhengende visuelt tema som fanger selskapets essens.",
        "required_elements": ["company_name", "tagline"],
    },
    "introduction": {
        "name": "Introduksjon",
        "prompt": "Gi en kort, engasjerende oppsummering av selskapet, med fokus på en krok som vekker interesse og forklarer selskapets kjerneverdier.",
        "required_elements": ["summary", "hook"],
    },
    # Add other slide types as needed
}

# Language configurations
LANGUAGE_CONFIGS = {
    "no": {
        "name": "Norwegian",
        "date_format": "%d.%m.%Y",
        "currency_format": "NOK %s",
        "is_default": True,
        "special_characters": "æøåÆØÅ"
    },
    "en": {
        "name": "English",
        "date_format": "%Y-%m-%d",
        "currency_format": "$%s",
        "is_default": False,
        "special_characters": ""
    }
}

# Function to get phase names based on language
def get_phase_names(language: str) -> List[str]:
    if language == "no":
        return PHASE_NAMES_NORWEGIAN
    return PHASE_NAMES_ENGLISH

# Function to get phase configurations based on language
def get_phase_configs(language: str) -> Dict[str, Dict]:
    if language == "no":
        return PHASE_CONFIGS_NORWEGIAN
    return PHASE_CONFIGS_ENGLISH

# Function to get slide template based on language
def get_slide_template(slide_type: str, language: str) -> Optional[Dict]:
    if language == "no":
        base_template = SLIDE_TYPES_NORWEGIAN.get(slide_type)
    else:
        base_template = SLIDE_TYPES_ENGLISH.get(slide_type)
    
    if not base_template:
        return None

    lang_config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS['en'])
    template = base_template.copy()
    template['language'] = lang_config
    template['original_language'] = language
    return template

# Function to get phase configuration based on language
def get_phase_config(phase_name: str, language: str = "en") -> Optional[Dict]:
    phase_configs = get_phase_configs(language)
    return phase_configs.get(phase_name)

# Function to get system message based on language
def get_system_message(message_type: str, language: str = "en", **kwargs) -> str:
    message_template = SYSTEM_MESSAGES.get(message_type, {}).get(language)
    if not message_template:
        message_template = SYSTEM_MESSAGES.get(message_type, {}).get('en', "")
    return message_template.format(**kwargs)


EDITING_MODES = {
    "structured": {
        "name": "Structured Feedback",
        "description": "Use predefined feedback options for each slide type",
        "allowed_operations": ["select_option", "provide_details"]
    },
    "guided": {
        "name": "Guided Editing",
        "description": "Step-by-step editing with AI assistance",
        "allowed_operations": ["modify_text", "regenerate", "translate"]
    }
}


EXPORT_CONFIGS = {
    "html": {
        "template_path": "templates/pitch_deck.html",
        "allowed_tags": ["h1", "h2", "p", "ul", "li", "strong", "em", "img"],
        "css_framework": "tailwind",
        "interactive": True
    },
    "pdf": {
        "page_size": "A4",
        "orientation": "landscape",
        "fonts": ["Arial", "Helvetica", "sans-serif"],
        "margin": {"top": 20, "right": 20, "bottom": 20, "left": 20}
    }
}