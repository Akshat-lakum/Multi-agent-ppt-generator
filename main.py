# main.py
# Final pipeline: Includes PDF conversion using LibreOffice.

from state_manager import StateManager
from agents.content_agent import ContentAgent
from agents.format_agent import FormatAgent
from agents.design_agent import DesignAgent
from agents.external_media_agent import ExternalMediaAgent
from agents.presentation_agent import PresentationAgent
import os
import time
import subprocess # Import the subprocess module

# The main pipeline function remains the same
def run_full_pipeline(pdf_path: str, theme_file: str, tone: str, slide_count: int, progress_callback=None):
    if not os.path.exists(pdf_path):
        print(f"ERROR: Input PDF not found at '{pdf_path}'.")
        return None

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

    if progress_callback: progress_callback("Step 1/5: Understanding content with AI...")
    content_agent.run()

    if progress_callback: progress_callback("Step 2/5: Planning slide structure...")
    format_agent.run()

    if progress_callback: progress_callback("Step 3/5: Applying design theme...")
    design_agent.run()

    if progress_callback: progress_callback("Step 4/5: Generating/Fetching visuals...")
    media_agent.run()

    if progress_callback: progress_callback("Step 5/5: Building final presentation...")
    presentation_agent.run()

    # --- RE-ADD PDF CONVERSION STEP using LibreOffice ---
    pptx_path = sm.get("output_path")
    pdf_output_path = None # Variable to store the final PDF path
    if pptx_path and os.path.exists(pptx_path):
        if progress_callback: progress_callback("Converting to PDF...")
        else: print("Converting to PDF using LibreOffice...")
        
        output_dir = os.path.dirname(pptx_path)
        try:
            # On Windows, the command might be 'soffice' instead of 'libreoffice'
            commands_to_try = [
                ['soffice', '--headless', '--convert-to', 'pdf', pptx_path, '--outdir', output_dir],
                ['libreoffice', '--headless', '--convert-to', 'pdf', pptx_path, '--outdir', output_dir]
            ]
            
            command_success = False
            for cmd in commands_to_try:
                try:
                    # Run the command, wait for it to complete, capture output
                    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60) # Added timeout
                    pdf_output_path = pptx_path.replace(".pptx", ".pdf")
                    if progress_callback: progress_callback(f"Successfully converted to PDF: {os.path.basename(pdf_output_path)}")
                    else: print(f"Successfully converted to PDF: {pdf_output_path}")
                    command_success = True
                    break # Exit loop if a command succeeds
                except FileNotFoundError:
                    # This means the command (soffice or libreoffice) wasn't found in PATH
                    continue
                except subprocess.TimeoutExpired:
                     print(f"Conversion timed out with '{cmd[0]}'.")
                     continue
                except subprocess.CalledProcessError as e:
                    # This means the command ran but reported an error
                    print(f"Error during conversion with '{cmd[0]}': {e.stderr.decode()}")
                    continue

            if not command_success:
                 if progress_callback: progress_callback("PDF Conversion Failed: LibreOffice not found or PATH not set correctly.")
                 else: print("Could not convert to PDF. Ensure LibreOffice is installed and its 'program' directory is in your system PATH.")

        except Exception as e:
            if progress_callback: progress_callback(f"PDF Conversion Failed: An unexpected error occurred.")
            else: print(f"An unexpected error occurred during PDF conversion: {e}")
    # -----------------------------

    end_time = time.time()
    print(f"Pipeline finished in {end_time - start_time:.2f} seconds.")
    
    # Return both paths if conversion was successful, otherwise just the pptx path
    return pptx_path, pdf_output_path if command_success else None

# Update the main execution block if needed
if __name__ == "__main__":
    default_pdf = "data/syllabus.pdf"
    print("--- Running Multi-Agent PPT Generation Pipeline (from command line) ---")
    pptx_file, pdf_file = run_full_pipeline(
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