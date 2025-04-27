import streamlit as st

def download_screen():
    """Display the download screen where the user can download the generated PowerPoint."""
    st.header("Download Your Presentation")
    if not st.session_state.generated_ppt:
        st.warning("No presentation has been generated. Please go back and create your presentation.")
        if st.button("Back to Content Review"):
            st.session_state.stage = "content"
            st.rerun()
        return
    # Success message and presentation details
    st.success("Your PowerPoint presentation has been successfully generated!")
    st.markdown(f"""
    ### Presentation Details:
    - **Topic:** {st.session_state.topic}
    - **Delivery Medium:** {st.session_state.delivery_medium}
    - **Complexity Level:** {st.session_state.complexity_level}
    - **Number of Slides:** {len(st.session_state.edited_structure)}
    """)
    # Prepare download button for the PowerPoint file
    topic_filename = st.session_state.topic.replace(" ", "_").lower() or "presentation"
    download_filename = f"slidedeck_{topic_filename}.pptx"
    st.download_button(
        label="Download PowerPoint Presentation",
        data=st.session_state.generated_ppt,
        file_name=download_filename,
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    # Additional guidance for next steps
    st.markdown("### What's Next?")
    st.markdown("""
    - Open the downloaded presentation in PowerPoint for final editing.  
    - Add or adjust images as needed.  
    - Customize slide design (colors, fonts) to match your branding.  
    - Practice your delivery with the generated slides.
    """)
    # Button to start a new presentation workflow
    if st.button("Create Another Presentation"):
        # Reset all session state variables for a fresh start
        st.session_state.slide_structure = []
        st.session_state.slide_contents = []
        st.session_state.edited_structure = []
        st.session_state.generated_ppt = None
        st.session_state.topic = ""
        st.session_state.delivery_medium = ""
        st.session_state.complexity_level = ""
        st.session_state.reference_text = ""
        st.session_state.stage = "input"
        st.rerun()
