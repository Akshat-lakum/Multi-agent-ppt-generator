# app.py
# The Streamlit GUI with theme selection.

import streamlit as st
from main import run_full_pipeline
import os

st.set_page_config(
    page_title="AI PPT Generator",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Multi-Agent Presentation Generator")
st.markdown("Upload a syllabus PDF and let our AI agents create a complete presentation for you. Customize the tone, length, and design to fit your needs.")

# --- Dictionary of available themes ---
# Maps user-friendly names to the actual filenames
THEMES = {
    "Edutor Blue (Default)": "edutor_theme.pptx",
    "Dark Mode": "dark_mode.pptx",
    "Minimalist": "minimalist.pptx",
}

# --- Sidebar for Customization Options ---
with st.sidebar:
    st.header("⚙️ Customization Options")
    
    # NEW: Theme selection dropdown
    theme_name = st.selectbox(
        "Select a presentation theme:",
        options=list(THEMES.keys())
    )
    selected_theme_file = THEMES[theme_name]

    tone = st.selectbox(
        "Select the content tone:",
        ("Beginner", "Intermediate", "Expert"),
        index=0
    )

    slide_count = st.slider(
        "Select approximate number of content slides:",
        min_value=5,
        max_value=20,
        value=10
    )

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose a syllabus PDF file", type="pdf")

if uploaded_file is not None:
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    if st.button("✨ Generate Presentation", type="primary"):
        
        progress_text = st.empty()
        
        def update_progress(message):
            progress_text.text(message)

        with st.spinner("The AI agents are hard at work... This may take a minute or two."):
            try:
                # Pass the selected theme file to the pipeline
                final_pptx_path = run_full_pipeline(
                    pdf_path=temp_pdf_path,
                    theme_file=selected_theme_file, # Pass the new theme option
                    tone=tone,
                    slide_count=slide_count,
                    progress_callback=update_progress
                )
                
                if final_pptx_path and os.path.exists(final_pptx_path):
                    st.success("🎉 Presentation generated successfully!")
                    
                    with open(final_pptx_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Presentation",
                            data=file,
                            file_name=os.path.basename(final_pptx_path),
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        )
                else:
                    st.error("Something went wrong. The presentation could not be generated.")
            except Exception as e:
                st.error(f"An error occurred: {e}")