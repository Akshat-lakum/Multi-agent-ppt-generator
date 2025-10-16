# agents/design_agent.py
# DesignAgent → reads the user's theme choice and sets the correct template path.

from .base_agent import BaseAgent
import os

class DesignAgent(BaseAgent):
    """
    Sets the presentation design by reading the selected theme file
    from the shared state and creating the full path to the template.
    """

    def run(self):
        self.log("Setting presentation design theme...")

        # Read the selected theme filename from the shared state
        theme_file = self.sm.get("theme_file")
        if not theme_file:
            self.log("WARNING: No theme file selected. Defaulting to 'edutor_theme.pptx'.")
            theme_file = "edutor_theme.pptx"

        # Construct the full path to the template
        template_path = os.path.join("templates", theme_file)

        if not os.path.exists(template_path):
            self.log(f"WARNING: Template file '{template_path}' not found. A default presentation will be created.")
            template_path = None

        # The 'theme_name' is now dynamic based on the selected file
        design_config = {
            "template_path": template_path,
            "theme_name": theme_file 
        }

        self.update_state("design", design_config)
        self.log(f"Design theme set to '{design_config['theme_name']}'.")
        self.sm.save("shared_state_after_design.json")



















































































































































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


