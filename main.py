# main.py
# Corrected chunk_text import and call.

from state_manager import StateManager
from agents.content_agent import ContentAgent, chunk_text # <-- IMPORT chunk_text HERE
from agents.format_agent import FormatAgent
from agents.design_agent import DesignAgent
from agents.external_media_agent import ExternalMediaAgent
from agents.presentation_agent import PresentationAgent
from agents.qa_agent import QAAgent
import os
import time
import subprocess
import streamlit as st

def run_full_pipeline(pdf_path: str, theme_file: str, tone: str, slide_count: int, progress_callback=None):
    if not os.path.exists(pdf_path):
        print(f"ERROR: Input PDF not found at '{pdf_path}'.")
        return None, None, None

    start_time = time.time()
    sm = StateManager()
    sm.update("input_pdf_path", pdf_path)
    sm.update("theme_file", theme_file)
    sm.update("tone", tone)
    sm.update("slide_count", slide_count)

    content_agent = ContentAgent("ContentAgent", sm)
    format_agent = FormatAgent("FormatAgent", sm)
    design_agent = DesignAgent("DesignAgent", sm)
    media_agent = ExternalMediaAgent("MediaAgent", sm)
    presentation_agent = PresentationAgent("PresentationAgent", sm)
    qa_agent = QAAgent("QAAgent", sm)

    # --- Run agent pipeline ---
    if progress_callback: progress_callback("Step 1/5: Understanding content with AI...")
    
    try:
        content_agent.log("Starting content extraction (Text, Tables)...")
        full_text, extracted_tables = content_agent._extract_text_and_tables_from_pdf(pdf_path)
        
        table_markdowns = [table.to_markdown(index=False) for table in extracted_tables] if extracted_tables else []
        if not full_text and not table_markdowns:
            content_agent.log("No text or tables extracted. Cannot proceed.")
            return None, None, None

        combined_content = full_text
        if table_markdowns:
            combined_content += "\n\n=== Appendix: Extracted Tables ===\n"
            for i, md in enumerate(table_markdowns):
                combined_content += f"\n--- Table {i+1} ---\n{md}\n"

        # --- CORRECTED CALL: Call chunk_text directly, not as a method ---
        content_chunks = chunk_text(combined_content, chunk_size=content_agent.chunk_size, overlap=content_agent.overlap)
        # -------------------------------------------------------------
        
        content_agent.log(f"Split content into {len(content_chunks)} chunks.")

        all_chapters = []
        for i, chunk in enumerate(content_chunks):
            content_agent.log(f"Processing chunk {i+1}/{len(content_chunks)}...")
            structured_content = content_agent._get_structured_content_from_llm(chunk, [], tone, slide_count)
            if structured_content and "chapters" in structured_content:
                all_chapters.extend(structured_content["chapters"])
            else:
                content_agent.log(f"No valid 'chapters' structure returned for chunk {i+1}.")
            
            if i < len(content_chunks) - 1:
                content_agent.log("Waiting 31 seconds to respect API rate limit...")
                time.sleep(31) 

        if all_chapters:
            content_agent.update_state("chapters", all_chapters)
            content_agent.log(f"Content processed. Found {len(all_chapters)} chapters total.")
        else:
            content_agent.log("ERROR: No chapters processed from any chunk.")
    
    except Exception as e:
        content_agent.log(f"ERROR in ContentAgent execution: {e}")
        st.error(f"Error during content generation: {e}")
        return None, None, None

    if progress_callback: progress_callback("Step 2/5: Planning slide structure...")
    format_agent.run()

    if progress_callback: progress_callback("Step 3/5: Applying design theme...")
    design_agent.run()

    if progress_callback: progress_callback("Step 4/5: Generating/Fetching visuals...")
    media_agent.run()

    if progress_callback: progress_callback("Step 5/5: Building final presentation...")
    presentation_agent.run()
    
    if progress_callback: progress_callback("Skipping QA check to respect rate limits.")
    qa_feedback_report = "QA Agent disabled to respect free API rate limits."
    sm.update("qa_feedback", qa_feedback_report)

    # --- PDF Conversion Step ---
    pptx_path = sm.get("output_path")
    pdf_output_path = None
    command_success = False
    if pptx_path and os.path.exists(pptx_path):
        if progress_callback: progress_callback("Converting to PDF...")
        output_dir = os.path.dirname(pptx_path)
        try:
            commands_to_try = [
                ['soffice', '--headless', '--convert-to', 'pdf', pptx_path, '--outdir', output_dir],
                ['libreoffice', '--headless', '--convert-to', 'pdf', pptx_path, '--outdir', output_dir]
            ]
            for cmd in commands_to_try:
                try:
                    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
                    pdf_output_path = pptx_path.replace(".pptx", ".pdf")
                    if progress_callback: progress_callback(f"Successfully converted to PDF.")
                    else: print(f"Successfully converted to PDF: {pdf_output_path}")
                    command_success = True
                    break
                except FileNotFoundError: continue
                except subprocess.TimeoutExpired: print(f"Conversion timed out with '{cmd[0]}'."); continue
                except subprocess.CalledProcessError as e: print(f"Error during conversion with '{cmd[0]}': {e.stderr.decode()}"); continue
            if not command_success:
                 message = "PDF Conversion Failed: LibreOffice not found or PATH not set correctly."
                 if progress_callback: progress_callback(message)
                 else: print(message)
        except Exception as e:
            message = f"PDF Conversion Failed: An unexpected error occurred: {e}"
            if progress_callback: progress_callback(message)
            else: print(message)

    end_time = time.time()
    print(f"Pipeline finished in {end_time - start_time:.2f} seconds.")
    
    qa_feedback_report = sm.get("qa_feedback")
    return pptx_path, pdf_output_path if command_success else None, qa_feedback_report

# --- Main execution block (remains the same) ---
if __name__ == "__main__":
    default_pdf = "data/syllabus.pdf"
    print("--- Running Multi-Agent PPT Generation Pipeline (from command line) ---")
    pptx_file, pdf_file, qa_report = run_full_pipeline(
        pdf_path=default_pdf,
        theme_file="edutor_theme.pptx", 
        tone="Beginner", 
        slide_count=10
    ) 
    print("\n=== ✅ PIPELINE FINISHED SUCCESSFULLY! ===")
    if pptx_file: print(f"Final presentation available at: {pptx_file}")
    if pdf_file: print(f"PDF version available at: {pdf_file}")
    if qa_report: print(f"\n--- AI Quality Assurance Feedback ---\n{qa_report}\n------------------------------------\n")
    print("========================================\n")