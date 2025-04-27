import os
from dotenv import load_dotenv

# Load environment variables (e.g., API keys) from .env file
load_dotenv()

import streamlit as st
from ui.input_screen import input_selection_screen
from ui.structure_screen import slide_structure_screen
from ui.content_screen import content_generation_screen
from ui.download_screen import download_screen

# Configure the Streamlit app page
st.set_page_config(
    page_title="SlideDeck: Smart Lecture Slide Generator",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("SlideDeck: Smart Lecture Slide Generator")
st.markdown("""
An intelligent platform designed to assist university lecturers in seamlessly generating formal, high-quality lecture presentations.
""")

# Initialize session state variables if not already set
if 'slide_structure' not in st.session_state:
    st.session_state.slide_structure = []
if 'slide_contents' not in st.session_state:
    st.session_state.slide_contents = []
if 'edited_structure' not in st.session_state:
    st.session_state.edited_structure = []
if 'generated_ppt' not in st.session_state:
    st.session_state.generated_ppt = None
if 'topic' not in st.session_state:
    st.session_state.topic = ""
if 'delivery_medium' not in st.session_state:
    st.session_state.delivery_medium = ""
if 'complexity_level' not in st.session_state:
    st.session_state.complexity_level = ""
if 'reference_text' not in st.session_state:
    st.session_state.reference_text = ""
if 'stage' not in st.session_state:
    st.session_state.stage = "input"  # Possible stages: input, structure, content, download

# Sidebar content
with st.sidebar:
    st.header("About SlideDeck")
    st.markdown("""
    SlideDeck uses AI to help you create professional lecture slides quickly and efficiently.
    
    **How it works:**
    1. Enter a topic or upload reference materials  
    2. Review and edit the slide structure  
    3. Generate complete presentation content  
    4. Download your PowerPoint file  
    
    **Features:**
    - Automatic slide structure generation  
    - Content creation with academic focus  
    - Diagrams and visual aids  
    - Professional formatting
    """)

    # Progress indicator in the sidebar
    st.header("Progress")
    progress_options = ["Input Selection", "Slide Structure", "Content Generation", "Download"]
    current_stage_index = ["input", "structure", "content", "download"].index(st.session_state.stage)
    for i, option in enumerate(progress_options):
        if i < current_stage_index:
            st.success(f"✓ {option}")
        elif i == current_stage_index:
            st.info(f"→ {option}")
        else:
            st.text(f"  {option}")

# Main content area: render appropriate screen based on current stage
if st.session_state.stage == "input":
    input_selection_screen()
elif st.session_state.stage == "structure":
    slide_structure_screen()
elif st.session_state.stage == "content":
    content_generation_screen()
elif st.session_state.stage == "download":
    download_screen()
