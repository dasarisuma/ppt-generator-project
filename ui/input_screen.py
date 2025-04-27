import time
import streamlit as st
from core.slide_generator import SlideGenerator

def input_selection_screen():
    """Display the input selection screen for topic input."""
    st.header("Input Selection")
    
    # Text input for lecture topic
    st.session_state.topic = st.text_input("Lecture Topic", value=st.session_state.topic)
    
    # Two columns for selecting delivery medium and complexity level
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.delivery_medium = st.selectbox(
            "Delivery Medium",
            ["In-person Lecture", "Online Lecture", "Workshop", "Tutorial Session"],
            index=0 if not st.session_state.delivery_medium else 
                  ["In-person Lecture", "Online Lecture", "Workshop", "Tutorial Session"].index(st.session_state.delivery_medium)
        )
    with col2:
        st.session_state.complexity_level = st.selectbox(
            "Complexity Level",
            ["Basic", "Intermediate", "Advanced"],
            index=0 if not st.session_state.complexity_level else 
                  ["Basic", "Intermediate", "Advanced"].index(st.session_state.complexity_level)
        )
    
    # Button to generate slide structure from the given topic
    if st.button("Generate Slide Structure"):
        if st.session_state.topic:
            with st.spinner("Generating slide structure..."):
                time.sleep(2)  # simulate processing delay
                slide_generator = SlideGenerator()
                st.session_state.slide_structure = slide_generator.generate_slide_structure(
                    st.session_state.topic,
                    st.session_state.delivery_medium,
                    st.session_state.complexity_level
                )
                st.session_state.edited_structure = st.session_state.slide_structure.copy()
                # Clear any reference text from previous runs
                st.session_state.reference_text = ""
                # Advance to the structure editing stage
                st.session_state.stage = "structure"
                st.rerun()
        else:
            st.error("Please enter a lecture topic.")