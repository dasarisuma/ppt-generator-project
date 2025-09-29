import time
import streamlit as st
from core.slide_generator import SlideGenerator

def content_generation_screen():
    
    st.header("Generated Slide Content")
    if not st.session_state.slide_contents or not st.session_state.edited_structure:
        st.warning("No slide content available. Please go back and generate content first.")
        if st.button("Back to Slide Structure"):
            st.session_state.stage = "structure"
            st.rerun()
        return
    st.markdown(f"""
    Review the generated content for your lecture slides on **{st.session_state.topic}**.  
    The content includes text, bullet points, and descriptions for diagrams or images that will appear in the final presentation.
    """)
    # Show each slide's content in an expandable section
    for slide, content in zip(st.session_state.edited_structure, st.session_state.slide_contents):
        slide_num = slide.get('slide_number', '?')
        slide_title = slide.get('slide_title', 'Untitled')
        slide_type = slide.get('slide_type', '')
        expander_label = f"Slide {slide_num}: {slide_title} ({slide_type})"
        with st.expander(expander_label):
            if slide_type == "title_slide":
                st.markdown(f"### {content.get('title', slide_title)}")
                st.markdown(f"*{content.get('subtitle', '')}*")
                st.markdown(f"{content.get('professor', '')}")
                st.markdown(f"{content.get('affiliation', '')}")
            elif slide_type in ["content_slide", "bullet_point_slide"]:
                st.subheader(slide_title)
                for point in content.get('main_content', []):
                    st.markdown(f"- {point}")
                if content.get('needs_image'):
                    st.markdown("---")
                    st.markdown("**Visual Aid:** An image will be generated for this slide with the following description:")
                    st.markdown(f"*{content.get('image_description', '')}*")
            elif slide_type == "diagram_slide":
                st.subheader(slide_title)
                intro = content.get('introduction', '')
                if intro:
                    st.markdown(intro)
                if content.get('key_points'):
                    st.markdown("**Key Points:**")
                    for point in content.get('key_points', []):
                        st.markdown(f"- {point}")
                st.markdown("---")
                st.markdown("**Diagram:** A diagram will be generated with the following description:")
                st.markdown(f"*{content.get('diagram_description', '')}*")
            elif slide_type == "conclusion_slide":
                st.subheader(slide_title)
                if content.get('takeaways'):
                    st.markdown("**Key Takeaways:**")
                    for point in content['takeaways']:
                        st.markdown(f"- {point}")
                if content.get('importance'):
                    st.markdown(f"**Importance:** {content.get('importance')}")
                if content.get('further_exploration'):
                    st.markdown("**Further Exploration:**")
                    for point in content['further_exploration']:
                        st.markdown(f"- {point}")
            else:
                st.subheader(slide_title)
                # Generic slide: display all content fields
                for key, value in content.items():
                    if key in ["image_url", "needs_image", "image_description", "diagram_description"]:
                        continue
                    if isinstance(value, list):
                        st.markdown(f"**{key.replace('_', ' ').title()}:**")
                        for item in value:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
    # Button to generate the PowerPoint file
    if st.button("Generate PowerPoint"):
        with st.spinner("Creating PowerPoint presentation..."):
            time.sleep(4)
            slide_generator = SlideGenerator()
            ppt_bytes = slide_generator.create_powerpoint(
                st.session_state.edited_structure,
                st.session_state.slide_contents,
                st.session_state.topic
            )
            st.session_state.generated_ppt = ppt_bytes
            st.session_state.stage = "download"
            st.rerun()
    # Navigation button to go back and refine content if needed
    if st.button("← Back to Slide Structure"):
        st.session_state.stage = "structure"
        st.rerun()
