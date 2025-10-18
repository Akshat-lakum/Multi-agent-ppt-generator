# app.py
# Updated Streamlit GUI to handle both PPTX and PDF outputs.

import streamlit as st
from main import run_full_pipeline # Import our updated pipeline function
import os

st.set_page_config(
    page_title="AI PPT Generator",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Multi-Agent Presentation Generator")
st.markdown("Upload a syllabus PDF and let our AI agents create a complete presentation for you. Customize the tone, length, and design to fit your needs.")

THEMES = {
    "Edutor Blue (Default)": "edutor_theme.pptx",
    "Dark Mode": "dark_mode.pptx",
    "Minimalist": "minimalist.pptx",
}

with st.sidebar:
    st.header("⚙️ Customization Options")
    theme_name = st.selectbox("Select a presentation theme:", options=list(THEMES.keys()))
    selected_theme_file = THEMES[theme_name]
    tone = st.selectbox("Select the content tone:", ("Beginner", "Intermediate", "Expert"), index=0)
    slide_count = st.slider("Select approximate number of content slides:", min_value=5, max_value=20, value=10)

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
                # --- Run the pipeline, which now returns two paths ---
                pptx_path, pdf_path = run_full_pipeline(
                    pdf_path=temp_pdf_path,
                    theme_file=selected_theme_file,
                    tone=tone,
                    slide_count=slide_count,
                    progress_callback=update_progress
                )
                
                # --- Provide download buttons based on generated files ---
                if pptx_path and os.path.exists(pptx_path):
                    st.success("🎉 Presentation generated successfully!")
                    
                    col1, col2 = st.columns(2) # Create columns for buttons
                    
                    with col1:
                        with open(pptx_path, "rb") as file:
                            st.download_button(
                                label="📥 Download PPTX",
                                data=file,
                                file_name=os.path.basename(pptx_path),
                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            )
                    
                    if pdf_path and os.path.exists(pdf_path):
                        with col2:
                            with open(pdf_path, "rb") as file:
                                st.download_button(
                                    label="📄 Download PDF",
                                    data=file,
                                    file_name=os.path.basename(pdf_path),
                                    mime="application/pdf",
                                )
                    else:
                        st.warning("PDF conversion failed. Check logs for details.")
                        
                else:
                    st.error("Something went wrong. The presentation could not be generated.")

            except Exception as e:
                st.error(f"An error occurred: {e}")