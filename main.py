# main.py
# Updated pipeline to return the QA feedback.

from state_manager import StateManager
from agents.content_agent import ContentAgent
from agents.format_agent import FormatAgent
from agents.design_agent import DesignAgent
from agents.external_media_agent import ExternalMediaAgent
from agents.presentation_agent import PresentationAgent
from agents.qa_agent import QAAgent
import os
import time
import subprocess

# The function now returns three values: pptx_path, pdf_path, qa_feedback
def run_full_pipeline(pdf_path: str, theme_file: str, tone: str, slide_count: int, progress_callback=None):
    if not os.path.exists(pdf_path):
        print(f"ERROR: Input PDF not found at '{pdf_path}'.")
        return None, None, None # Return None for all three paths/values

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

    # --- Run agent pipeline (remains the same) ---
    if progress_callback: progress_callback("Step 1/6: Understanding content with AI...")
    content_agent.run()

    if progress_callback: progress_callback("Step 2/6: Planning slide structure...")
    format_agent.run()

    if progress_callback: progress_callback("Step 3/6: Applying design theme...")
    design_agent.run()

    if progress_callback: progress_callback("Step 4/6: Generating/Fetching visuals...")
    media_agent.run()

    if progress_callback: progress_callback("Step 5/6: Building final presentation...")
    presentation_agent.run()
    
    if sm.get("slides"):
        if progress_callback: progress_callback("Step 6/6: Performing AI Quality Check...")
        qa_agent.run()
    else:
        print("Skipping QA step as slide generation failed earlier.")

    # --- PDF Conversion Step (remains the same) ---
    pptx_path = sm.get("output_path")
    pdf_output_path = None
    command_success = False
    if pptx_path and os.path.exists(pptx_path):
        if progress_callback: progress_callback("Converting to PDF...")
        else: print("Converting to PDF using LibreOffice...")
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
    
    # --- UPDATED RETURN STATEMENT ---
    # Get the QA feedback from the state
    qa_feedback_report = sm.get("qa_feedback")
    # Return all three results
    return pptx_path, pdf_output_path if command_success else None, qa_feedback_report

# --- Main execution block updated to handle three return values ---
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
    if pptx_file:
        print(f"Final presentation available at: {pptx_file}")
    if pdf_file:
        print(f"PDF version available at: {pdf_file}")
    if qa_report:
        print("\n--- AI Quality Assurance Feedback ---")
        print(qa_report)
        print("------------------------------------\n")
    print("========================================\n")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



# # # main.py
# # # Full pipeline: Content -> Format -> Design -> Presentation

# # from state_manager import StateManager
# # from agents.content_agent import ContentAgent
# # from agents.format_agent import FormatAgent
# # from agents.design_agent import DesignAgent
# # from agents.presentation_agent import PresentationAgent

# # def run_full_pipeline():
# #     """
# #     Initializes and runs the complete agent pipeline to generate a presentation.
# #     """
# #     sm = StateManager()

# #     content_agent = ContentAgent("ContentAgent", sm)
# #     format_agent = FormatAgent("FormatAgent", sm)
# #     design_agent = DesignAgent("DesignAgent", sm)
# #     presentation_agent = PresentationAgent(sm)

# #     print("Running Content Agent...")
# #     content_agent.run()
    
# #     print("\nRunning Format Agent...")
# #     format_agent.run()
    
# #     print("\nRunning Design Agent...")
# #     design_agent.run()

# #     print("\nRunning Presentation Agent...")
# #     presentation_agent.build_presentation()

# #     print("\n=== Pipeline Finished ===")
# #     slides = sm.get("slides") or []
# #     design = sm.get("design") or {}
# #     print(f"Slides count: {len(slides)}")
# #     print(f"Design styles assigned: {len(design)}")
# #     print("=========================\n")


# # if __name__ == "__main__":
# #     run_full_pipeline()

# # ______________________________________________________________________________________________
# #final dummy test 
# # main.py
# # Full pipeline: Content -> Format -> Design -> Presentation

# from state_manager import StateManager
# from agents.content_agent import ContentAgent
# from agents.format_agent import FormatAgent
# from agents.design_agent import DesignAgent
# from agents.presentation_agent import PresentationAgent

# def run_full_pipeline():
#     """
#     Initializes and runs the complete agent pipeline to generate a presentation.
#     """
#     # 1. Initialize the shared state
#     sm = StateManager()

#     # 2. Instantiate all agents
#     content_agent = ContentAgent("ContentAgent", sm)
#     format_agent = FormatAgent("FormatAgent", sm)
#     design_agent = DesignAgent("DesignAgent", sm)
#     presentation_agent = PresentationAgent("PresentationAgent", sm)

#     # 3. Run agents sequentially
#     print("--- Starting Multi-Agent PPT Generation Pipeline ---")
    
#     content_agent.run()
#     print("-" * 20)
    
#     format_agent.run()
#     print("-" * 20)
    
#     design_agent.run()
#     print("-" * 20)
    
#     presentation_agent.run()
#     print("-" * 20)

#     # 4. Final summary
#     output_path = sm.get("output_path")
#     print("\n=== ✅ PIPELINE FINISHED SUCCESSFULLY! ===")
#     if output_path:
#         print(f"Final presentation is available at: {output_path}")
#     print("========================================\n")


# if __name__ == "__main__":
#     run_full_pipeline()