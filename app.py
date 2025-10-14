# app.py
# The Streamlit GUI for the Multi-Agent PPT Generator.

import streamlit as st
from main import run_full_pipeline # Import our pipeline function
import os
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="AI PPT Generator",
    page_icon="🤖",
    layout="centered"
)

# --- App Title and Description ---
st.title("🤖 AI Multi-Agent Presentation Generator")
st.markdown("Upload a syllabus PDF and let our AI agents create a complete presentation for you, complete with text, images, and structure.")

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose a syllabus PDF file", type="pdf")

if uploaded_file is not None:
    # --- Save the uploaded file temporarily ---
    # Create a temporary directory to store the uploaded file
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # --- Generate Presentation Button ---
    if st.button("✨ Generate Presentation", type="primary"):
        
        # --- Display a spinner and progress bar while the pipeline runs ---
        progress_text = st.empty()
        
        def update_progress(message):
            # This function will be called by our pipeline to update the UI
            progress_text.text(message)

        with st.spinner("The AI agents are hard at work... This may take a minute or two."):
            try:
                # --- Run the main pipeline ---
                final_pptx_path = run_full_pipeline(temp_pdf_path, update_progress)
                
                if final_pptx_path and os.path.exists(final_pptx_path):
                    st.success("🎉 Presentation generated successfully!")
                    
                    # --- Provide a download button for the generated file ---
                    with open(final_pptx_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Presentation",
                            data=file,
                            file_name=os.path.basename(final_pptx_path),
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        )
                else:
                    st.error("Something went wrong. The presentation could not be generated. Please check the logs.")

            except Exception as e:
                st.error(f"An error occurred: {e}")