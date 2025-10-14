# # agents/design_agent.py
# # DesignAgent → assigns dummy layouts, fonts, and color themes.

# from .base_agent import BaseAgent

# class DesignAgent(BaseAgent):
#     """
#     Dummy DesignAgent: Assigns layout, font, and color theme to each slide.
#     """

#     def run(self):
#         self.log("Starting dummy design assignment...")

#         slides = self.sm.get("slides")
#         if not slides:
#             self.log("No slides found! Aborting design phase.")
#             return

#         # Define dummy style templates
#         styles = {
#             "title": {"font": "Arial Bold", "color": "#1E90FF", "layout": "centered"},
#             "content": {"font": "Calibri", "color": "#000000", "layout": "text-left"},
#             "summary": {"font": "Georgia Italic", "color": "#228B22", "layout": "summary-style"}
#         }

#         design = {}

#         for slide in slides:
#             s_type = slide["type"]
#             if s_type in styles:
#                 design[slide["id"]] = styles[s_type]
#             else:
#                 design[slide["id"]] = {"font": "Times New Roman", "color": "#333333", "layout": "default"}

#         # Update shared state
#         self.update_state("design", design)
#         self.log(f"Dummy design styles assigned for {len(design)} slides.")

#_______________________________________________________________________________________
## full dymmy 
# agents/design_agent.py
# DesignAgent → sets the presentation theme and template.

from .base_agent import BaseAgent
import os

class DesignAgent(BaseAgent):
    """
    Sets the overall design theme for the presentation, primarily by specifying
    a template .pptx file to use.
    """

    def run(self):
        self.log("Setting presentation design theme...")

        # For a real implementation, this could involve more complex logic,
        # like choosing from multiple templates. For our dummy version,
        # we'll just define one.
        template_path = "templates/edutor_theme.pptx"

        # Check if the template exists, otherwise log a warning
        if not os.path.exists(template_path):
            self.log(f"WARNING: Template file not found at '{template_path}'. A default presentation will be created.")
            template_path = None # The presentation agent will handle this

        design_config = {
            "template_path": template_path,
            "theme_name": "Edutor Corporate Blue",
            "fonts": {
                "title": "Arial Black",
                "body": "Calibri"
            }
        }

        self.update_state("design", design_config)
        self.log(f"Design theme set to '{design_config['theme_name']}'.")
        self.sm.save("shared_state_after_design.json")