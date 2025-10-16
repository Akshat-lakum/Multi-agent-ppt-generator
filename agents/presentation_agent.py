# agents/presentation_agent.py
# Adding special debugging to find the source of the TypeError.

from .base_agent import BaseAgent
from pptx import Presentation
from pptx.util import Inches
import os

class PresentationAgent(BaseAgent):
    """
    Generates the final .pptx presentation, now with added debugging to
    catch and report the cause of the persistent TypeError.
    """

    def _delete_initial_slide(self, prs, slides_plan):
        while len(prs.slides) > len(slides_plan):
            xml_slides = prs.slides._sldIdLst  
            to_remove = xml_slides[0]
            xml_slides.remove(to_remove)
            self.log("Removed an initial blank slide.")

    def run(self):
        self.log("Starting final presentation generation...")
        slides_plan = self.sm.get("slides") or []
        design_config = self.sm.get("design")
        output_dir = "output"
        output_filename = "final_presentation.pptx"
        output_path = os.path.join(output_dir, output_filename)

        if not slides_plan:
            self.log("ERROR: No slides plan found. Aborting.")
            return

        template_path = design_config.get("template_path")
        try:
            prs = Presentation(template_path) if template_path and os.path.exists(template_path) else Presentation()
            self.log(f"Using template from: {template_path}" if template_path and os.path.exists(template_path) else "No valid template found. Creating default presentation.")
        except Exception as e:
            self.log(f"ERROR: Failed to load template '{template_path}'. Creating blank presentation. Details: {e}")
            prs = Presentation()

        layout_map = { "main_title": 0, "chapter_title": 0, "content_only": 1, "content_with_image": 8, "quiz": 1, "thank_you": 5 }

        for i, slide_data in enumerate(slides_plan):
            try: # --- START OF NEW DEBUGGING BLOCK ---
                slide_type = slide_data.get("type", "content")
                
                image_path = slide_data.get("image_path")
                layout_key = "content_only"

                # This is the line that is likely causing the error
                if slide_type == "content" and image_path and os.path.exists(image_path):
                    layout_key = "content_with_image"
                elif slide_type != "content":
                    layout_key = slide_type
                
                # ... (rest of the code is the same)

                layout_index = layout_map.get(layout_key, 1)
                slide_layout = prs.slide_layouts[layout_index]
                slide = prs.slides.add_slide(slide_layout)

                if hasattr(slide.shapes, 'title') and slide.shapes.title is not None:
                    slide.shapes.title.text = slide_data.get("title", "")

                if layout_key in ["main_title", "chapter_title"]:
                    if len(slide.placeholders) > 1:
                        slide.placeholders[1].text = slide_data.get("subtitle", "")
                
                elif layout_key in ["content_only", "quiz"]:
                    if len(slide.placeholders) > 1:
                        body_shape = slide.placeholders[1]
                        tf = body_shape.text_frame
                        tf.clear()
                        for bullet in slide_data.get("bullets", []):
                            p = tf.add_paragraph()
                            p.text = bullet
                            p.level = 0
                
                elif layout_key == "content_with_image":
                    if len(slide.placeholders) > 2:
                        text_placeholder = slide.placeholders[1]
                        tf = text_placeholder.text_frame
                        tf.clear()
                        for bullet in slide_data.get("bullets", []):
                            p = tf.add_paragraph()
                            p.text = bullet
                            p.level = 0
                        
                        image_placeholder = slide.placeholders[2]
                        slide.shapes.add_picture(
                            image_path,
                            image_placeholder.left, image_placeholder.top,
                            width=image_placeholder.width, height=image_placeholder.height
                        )
                        self.log(f"Added image {image_path} to slide.")
            
            except TypeError as e:
                self.log("--- !!! CRITICAL ERROR FOUND !!! ---")
                self.log(f"A TypeError occurred while processing slide number {i+1}.")
                self.log(f"Error details: {e}")
                self.log("This usually means 'image_path' is not a string.")
                self.log(f"Problematic slide_data: {slide_data}")
                self.log("------------------------------------")
                # Re-raise the exception to show it in the Streamlit UI
                raise e
            # --- END OF NEW DEBUGGING BLOCK ---

        self._delete_initial_slide(prs, slides_plan)
        os.makedirs(output_dir, exist_ok=True)
        prs.save(output_path)
        self.update_state("output_path", output_path)
        self.log(f"Presentation saved successfully to: {output_path}")











































































































































# from state_manager import StateManager
# from pptx import Presentation
# from pptx.util import Inches, Pt
# import logging
# import os

# class PresentationAgent:
#     def __init__(self, state: StateManager, output_path="output_ppt/final_presentation.pptx"):
#         self.state = state
#         self.output_path = output_path
#         logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] %(message)s')
#         self.logger = logging.getLogger("PresentationAgent")

#     def build_presentation(self):
#         self.logger.info("Starting presentation generation...")

#         # ✅ Correct way — StateManager.get() only takes one argument
#         slides = self.state.get("slides")
#         design = self.state.get("design")

#         # Provide safe defaults manually if None
#         if slides is None:
#             slides = []
#         if design is None:
#             design = {}

#         if not slides:
#             self.logger.warning("No slides found in shared state. Aborting presentation build.")
#             return

#         prs = Presentation()

#         for idx, slide_content in enumerate(slides):
#             slide_layout = prs.slide_layouts[1]  # Title + content layout
#             slide = prs.slides.add_slide(slide_layout)

#             title = slide.shapes.title
#             content = slide.placeholders[1]

#             title.text = slide_content.get("title", f"Slide {idx + 1}")
#             content.text = slide_content.get("content", "No content provided.")

#             # Optionally apply dummy design style
#             style = design.get(f"slide_{idx+1}", "Default Style")
#             self.logger.info(f"Applied design style '{style}' to slide {idx + 1}")

#         # Ensure output directory exists
#         os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

#         prs.save(self.output_path)
#         self.logger.info(f"Presentation saved at: {self.output_path}")

#_________________________________________________________________________________________
