# agents/presentation_agent.py
# Corrected PresentationAgent with the proper MsoAutoSize import.

from .base_agent import BaseAgent
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import MsoAutoSize # <-- CORRECTED IMPORT (Back to text)
import os
import streamlit as st # Import streamlit for error messages

class PresentationAgent(BaseAgent):
    """
    Generates the final .pptx presentation, handling layouts, images, notes,
    and attempting to auto-fit overflowing text.
    """

    def _delete_initial_slide(self, prs, slides_plan):
        # ... (delete_initial_slide remains the same)
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
            self.log("ERROR: No slides plan found. Aborting."); return

        template_path = design_config.get("template_path")
        try:
            prs = Presentation(template_path) if template_path and os.path.exists(template_path) else Presentation()
            self.log(f"Using template from: {template_path}" if template_path and os.path.exists(template_path) else "No valid template found. Creating default presentation.")
        except Exception as e:
            self.log(f"ERROR: Failed to load template '{template_path}'. {e}"); prs = Presentation()

        layout_map = { "main_title": 0, "chapter_title": 0, "content_only": 1, "content_with_image": 8, "quiz": 1, "thank_you": 5 }

        for slide_data in slides_plan:
            slide_type = slide_data.get("type", "content")
            image_path = slide_data.get("image_path")
            layout_key = "content_only"
            # Determine layout (robust check)
            if slide_type == "content" and image_path and os.path.exists(image_path):
                 layout_key = "content_with_image"
            elif slide_type != "content":
                 layout_key = slide_type

            layout_index = layout_map.get(layout_key, 1) # Default to content_only (layout 1)

            try:
                slide_layout = prs.slide_layouts[layout_index]
                slide = prs.slides.add_slide(slide_layout)
            except IndexError:
                self.log(f"WARNING: Layout index {layout_index} not found for type '{layout_key}'. Using default layout 1.");
                slide_layout = prs.slide_layouts[1]; slide = prs.slides.add_slide(slide_layout)

            # Add Speaker Notes (remains the same)
            if slide.has_notes_slide and slide_data.get("speaker_notes"):
                notes_slide = slide.notes_slide
                text_frame = notes_slide.notes_text_frame
                text_frame.clear(); p = text_frame.add_paragraph()
                p.text = slide_data.get("speaker_notes", "")
                # self.log(f"Added speaker notes to slide '{slide_data.get('title', '')}'.") # Optional log

            # Populate Title
            if hasattr(slide.shapes, 'title') and slide.shapes.title is not None:
                slide.shapes.title.text = slide_data.get("title", "")
                # Optionally add auto-fit for title too
                # slide.shapes.title.text_frame.auto_size = MsoAutoSize.TEXT_TO_FIT_SHAPE

            # Populate Content Placeholders
            if layout_key in ["main_title", "chapter_title"]:
                if len(slide.placeholders) > 1:
                    subtitle_placeholder = slide.placeholders[1]
                    subtitle_placeholder.text = slide_data.get("subtitle", "")
                    # Use MsoAutoSize.SHAPE_TO_FIT_TEXT which might be more reliable
                    subtitle_placeholder.text_frame.auto_size = MsoAutoSize.SHAPE_TO_FIT_TEXT

            elif layout_key in ["content_only", "quiz"]:
                if len(slide.placeholders) > 1:
                    body_shape = slide.placeholders[1]
                    tf = body_shape.text_frame
                    tf.clear()
                    tf.word_wrap = True
                    # Use MsoAutoSize.SHAPE_TO_FIT_TEXT
                    tf.auto_size = MsoAutoSize.SHAPE_TO_FIT_TEXT
                    # Optionally adjust font size if auto-size isn't enough
                    # for p in tf.paragraphs: p.font.size = Pt(16) # Example starting size
                    for bullet in slide_data.get("bullets", []):
                        p = tf.add_paragraph()
                        if isinstance(bullet, dict): p.text = bullet.get('question', '')
                        else: p.text = str(bullet)
                        p.level = 0
                        # p.font.size = Pt(16) # Match size if set above


            elif layout_key == "content_with_image":
                if len(slide.placeholders) > 2:
                    # Text placeholder (usually index 1)
                    text_placeholder = slide.placeholders[1]
                    tf = text_placeholder.text_frame
                    tf.clear()
                    tf.word_wrap = True
                    # Use MsoAutoSize.SHAPE_TO_FIT_TEXT
                    tf.auto_size = MsoAutoSize.SHAPE_TO_FIT_TEXT
                    # Optionally adjust font size
                    # for p in tf.paragraphs: p.font.size = Pt(14)
                    for bullet in slide_data.get("bullets", []):
                        p = tf.add_paragraph()
                        p.text = str(bullet)
                        p.level = 0
                        # p.font.size = Pt(14)

                    # Image placeholder (usually index 2)
                    image_placeholder = slide.placeholders[2]
                    if image_path and os.path.exists(image_path):
                        try:
                            slide.shapes.add_picture(
                                image_path,
                                image_placeholder.left, image_placeholder.top,
                                width=image_placeholder.width, height=image_placeholder.height
                            )
                            # self.log(f"Added image {image_path} to slide.") # Optional log
                        except Exception as img_e:
                             self.log(f"ERROR: Could not add picture {image_path}. {img_e}")

        self._delete_initial_slide(prs, slides_plan)
        os.makedirs(output_dir, exist_ok=True)
        try:
            prs.save(output_path)
            self.update_state("output_path", output_path)
            self.log(f"Presentation saved successfully to: {output_path}")
        except PermissionError:
             self.log(f"ERROR: Permission denied saving {output_path}. Is the file open?")
             st.error(f"Save failed: Please close {os.path.basename(output_path)} if it's open and try again.")
        except Exception as save_e:
             self.log(f"ERROR: Failed to save presentation. {save_e}")
             st.error(f"Failed to save presentation: {save_e}")





























































































































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
