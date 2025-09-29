import time
import streamlit as st
from core.slide_generator import SlideGenerator # Assuming SlideGenerator is in core

def slidestructure_screen():
    """Display the slide structure review and editing screen."""
    st.header("Review and Edit Slide Structure")

    # Ensure edited_structure exists in session state
    if 'edited_structure' not in st.session_state or not st.session_state.edited_structure:
        st.warning("No slide structure available. Please go back and generate a structure first.")
        if st.button("Back to Input Selection"):
            st.session_state.stage = "input"
            st.rerun()
        return

    st.markdown(f"""
    Review the generated slide structure for your lecture on **{st.session_state.topic}**.
    You can edit slide titles, change slide types, reorder slides, or add/remove slides as needed.
    """)

    # Define the complete list of valid slide types from slide_generator.py
    valid_slide_types = ["title_slide", "content_slide", "bullet_point_slide", "image_slide", "block_diagram_slide", "conclusion_slide"]

    # Create a temporary list to hold the edits for this run
    current_edits = []
    slides_to_remove_indices = set() # Keep track of indices to remove

    # Display each slide entry with editable fields
    for i, slide in enumerate(st.session_state.edited_structure):
        # Use a unique container for each slide to manage state correctly
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 1]) # Adjusted column widths

            with col1:
                # Use slide_number from the data, default to i+1 if missing
                order = st.number_input("Order", min_value=1, value=slide.get("slide_number", i + 1), key=f"num_{i}")

            with col2:
                title = st.text_input("Slide Title", value=slide.get("slide_title", ""), key=f"title_{i}")

                # --- *** THE FIX IS HERE *** ---
                current_type = slide.get("slide_type", "content_slide")
                # Ensure the current type is valid, default if not
                if current_type not in valid_slide_types:
                    st.warning(f"Slide {i+1} had an invalid type '{current_type}', defaulting to 'content_slide'.")
                    current_type = "content_slide"

                # Calculate the index based on the *full* valid list
                try:
                    type_index = valid_slide_types.index(current_type)
                except ValueError:
                    st.error(f"Error finding index for type '{current_type}'. Defaulting index.")
                    type_index = 1 # Default to 'content_slide' index

                # Use the full list for options and the calculated index
                slide_type = st.selectbox(
                    "Slide Type",
                    options=valid_slide_types, # Use the full list here
                    index=type_index,          # Use the correctly calculated index
                    key=f"type_{i}"
                )
                # --- *** END OF FIX *** ---

            with col3:
                st.write("") # spacer
                st.write("") # spacer
                # Use a callback or check button state to mark for removal
                if st.button("Remove", key=f"remove_{i}"):
                    # Mark this index for removal after the loop
                    slides_to_remove_indices.add(i)
                    # Rerun immediately to reflect removal intent visually
                    st.rerun()


            # Add the potentially edited slide data to our temporary list
            # Only add if not marked for removal in this iteration
            if i not in slides_to_remove_indices:
                 current_edits.append({
                    # Store original index to help with removal later if needed
                    "original_index": i,
                    "slide_number": int(order), # Keep user's order input for sorting
                    "slide_title": title,
                    "slide_type": slide_type
                })

        st.divider()

    # --- Process Removals and Updates ---
    final_structure = []
    # Filter out slides marked for removal based on original index
    if slides_to_remove_indices:
        st.warning(f"Removing {len(slides_to_remove_indices)} slide(s)...")
        temp_structure = []
        for i, slide_data in enumerate(st.session_state.edited_structure):
             if i not in slides_to_remove_indices:
                 temp_structure.append(slide_data)
        st.session_state.edited_structure = temp_structure
        # Clear removal set and rerun to update UI cleanly
        slides_to_remove_indices.clear()
        st.rerun() # Rerun to show the list without the removed items

    # If no removals happened in this run, update based on current edits
    else:
        # Sort the collected edits by the 'Order' input
        current_edits.sort(key=lambda x: x["slide_number"])
        # Re-number sequentially based on the sorted order
        for idx, slide_data in enumerate(current_edits):
            slide_data["slide_number"] = idx + 1
            # Remove the temporary original_index key before saving
            if "original_index" in slide_data:
                del slide_data["original_index"]
            final_structure.append(slide_data)

        # Update session state only if changes were made or structure exists
        # Compare with current state to avoid unnecessary updates/reruns
        if final_structure != st.session_state.edited_structure:
             st.session_state.edited_structure = final_structure
             # Optional: Could add a small success message here
             # st.toast("Structure updated.") # Use toast for less intrusive feedback
             # Avoid rerun here unless strictly necessary, let subsequent actions trigger it


    # --- Add New Slide Button ---
    if st.button("Add New Slide"):
        new_slide_num = 1
        if st.session_state.edited_structure: # Check if list is not empty
             new_slide_num = len(st.session_state.edited_structure) + 1

        new_slide = {
            "slide_number": new_slide_num,
            "slide_title": "New Slide Title",
            "slide_type": "content_slide"
        }
        # Append directly to the session state list
        st.session_state.edited_structure.append(new_slide)
        st.rerun() # Rerun to show the new slide fields

    # --- Navigation Buttons ---
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
    with col_nav1:
        if st.button("← Back to Input"):
            st.session_state.stage = "input"
            st.rerun()

    with col_nav3:
        # Use the latest structure from session state for the check
        if st.button("Generate Content →"):
            if st.session_state.edited_structure: # Check if structure is not empty
                # Use a context manager for the spinner
                with st.spinner("Generating slide content... This may take a moment."):
                    # Initialize generator (consider doing this earlier if reused)
                    try:
                        slide_generator = SlideGenerator()
                        # Ensure generator initialized correctly (check for groq_client)
                        if not slide_generator.groq_client:
                             st.error("Slide Generator failed to initialize properly. Check API keys/connections.")
                             # Prevent proceeding without a working generator
                             st.stop()

                        # Call the coordinated content generation method
                        final_structure, slide_contents = slide_generator.create_slides_with_content(
                            topic=st.session_state.topic,
                            delivery_medium=st.session_state.delivery_medium, # Assuming this exists
                            complexity_level=st.session_state.complexity_level
                            # reference_text=st.session_state.get('reference_text') # Optional
                        )

                        # Check if content generation was successful
                        if not slide_contents or len(slide_contents) != len(final_structure):
                             st.error("Content generation failed or produced incomplete results. Please review logs or try again.")
                             # Optionally display partial results or stay on this screen
                        else:
                            # Store both the potentially re-ordered structure and the generated content
                            st.session_state.edited_structure = final_structure # Save potentially re-ordered structure
                            st.session_state.slide_contents = slide_contents
                            st.session_state.stage = "content" # Move to the next stage
                            st.success("Content generated successfully!")
                            time.sleep(1) # Brief pause before rerun
                            st.rerun()

                    except Exception as e:
                         st.error(f"An error occurred during content generation: {e}")
                         # Log the full traceback for debugging if needed
                         st.exception(e)

            else:
                st.error("Please add at least one slide before generating content.")

# --- Example of how to call this function in your main app ---
# if __name__ == "__main__":
#     # Initialize session state variables needed for testing
#     if 'stage' not in st.session_state:
#         st.session_state.stage = "structure" # Start at this screen for testing
#     if 'topic' not in st.session_state:
#         st.session_state.topic = "Test Topic"
#     if 'complexity_level' not in st.session_state:
#         st.session_state.complexity_level = "Beginner"
#     if 'delivery_medium' not in st.session_state:
#         st.session_state.delivery_medium = "Online"
#     if 'edited_structure' not in st.session_state:
#         # Provide some sample initial structure for testing
#         st.session_state.edited_structure = [
#             {"slide_number": 1, "slide_title": "Intro", "slide_type": "title_slide"},
#             {"slide_number": 2, "slide_title": "Core Concept", "slide_type": "content_slide"},
#             {"slide_number": 3, "slide_title": "Visual Example", "slide_type": "image_slide"}, # Test new type
#             {"slide_number": 4, "slide_title": "Process Flow", "slide_type": "block_diagram_slide"}, # Test new type
#             {"slide_number": 5, "slide_title": "Summary", "slide_type": "conclusion_slide"},
#         ]
#
#     # Call the screen function
#     slide_structure_screen()