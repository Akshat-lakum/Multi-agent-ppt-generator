# main.py
# Refactored pipeline logic to be callable as a function.

from state_manager import StateManager
from agents.content_agent import ContentAgent
from agents.format_agent import FormatAgent
from agents.design_agent import DesignAgent
from agents.external_media_agent import ExternalMediaAgent
from agents.presentation_agent import PresentationAgent
import os
import time

# This function now contains the core logic of your application
def run_full_pipeline(pdf_path: str, progress_callback=None):
    """
    Initializes and runs the complete agent pipeline for a given PDF.
    Returns the path to the final presentation.
    """
    if not os.path.exists(pdf_path):
        print(f"ERROR: Input PDF not found at '{pdf_path}'.")
        return None
        
    start_time = time.time()
    
    # 1. Initialize the shared state
    sm = StateManager()
    sm.update("input_pdf_path", pdf_path)

    # 2. Instantiate all agents
    content_agent = ContentAgent("ContentAgent", sm)
    format_agent = FormatAgent("FormatAgent", sm)
    design_agent = DesignAgent("DesignAgent", sm)
    media_agent = ExternalMediaAgent("MediaAgent", sm)
    presentation_agent = PresentationAgent("PresentationAgent", sm)

    # 3. Run agents sequentially, with progress updates
    if progress_callback: progress_callback("Step 1/5: Understanding content with AI...")
    content_agent.run()
    
    if progress_callback: progress_callback("Step 2/5: Planning slide structure...")
    format_agent.run()
    
    if progress_callback: progress_callback("Step 3/5: Applying design theme...")
    design_agent.run()
    
    if progress_callback: progress_callback("Step 4/5: Searching for images...")
    media_agent.run()
    
    if progress_callback: progress_callback("Step 5/5: Building final presentation...")
    presentation_agent.run()

    end_time = time.time()
    print(f"Pipeline finished in {end_time - start_time:.2f} seconds.")
    
    # 4. Return the path of the generated file
    return sm.get("output_path")

# This part allows you to still run main.py from the command line if you want
if __name__ == "__main__":
    # The default PDF to use when running directly
    default_pdf = "data/syllabus.pdf"
    print("--- Running Multi-Agent PPT Generation Pipeline (from command line) ---")
    output_file = run_full_pipeline(default_pdf)
    if output_file:
        print(f"\n=== ✅ PIPELINE FINISHED SUCCESSFULLY! ===")
        print(f"Final presentation is available at: {output_file}")
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