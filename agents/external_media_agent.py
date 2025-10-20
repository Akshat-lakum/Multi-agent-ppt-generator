# agents/external_media_agent.py
# MediaAgent can now generate placeholder charts, diagrams, or fetch photos.

from .base_agent import BaseAgent
from dotenv import load_dotenv
import os
import requests
import graphviz
import matplotlib.pyplot as plt # Import Matplotlib
import seaborn as sns # Import Seaborn
import pandas as pd # Import Pandas
import numpy as np # Import Numpy for placeholder data

class ExternalMediaAgent(BaseAgent):
    """
    Chooses the best visual for a slide, prioritizing:
    1. Generates a placeholder chart from AI suggestion.
    2. Generates a diagram from DOT code.
    3. Fetches a stock photo from Pexels.
    """
    def __init__(self, name, state_manager, config=None):
        super().__init__(name, state_manager)
        load_dotenv()
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        # Removed the warning here to keep logs cleaner
        self.assets_dir = "assets"
        os.makedirs(self.assets_dir, exist_ok=True)
        # Set a default Seaborn style for better looking charts
        sns.set_theme(style="whitegrid")

    def _generate_placeholder_chart(self, suggestion: dict, slide_id: str) -> str | None:
        """Generates a placeholder chart image based on AI suggestion."""
        chart_type = suggestion.get("type", "bar")
        title = suggestion.get("title", "Placeholder Chart")
        self.log(f"Generating placeholder '{chart_type}' chart for slide {slide_id}: '{title}'")
        
        # Create placeholder data
        # For simplicity, we'll use generic categories/values
        try:
            plt.figure(figsize=(8, 4)) # Create a figure
            
            if chart_type == "bar":
                categories = ['Category A', 'Category B', 'Category C', 'Category D']
                values = np.random.randint(20, 100, size=len(categories))
                sns.barplot(x=categories, y=values, palette="viridis")
            elif chart_type == "line":
                x_values = np.arange(1, 11)
                y_values = np.random.rand(10) * 50 + 50 # Example trend
                sns.lineplot(x=x_values, y=y_values, marker='o')
                plt.xlabel("Time/Sequence")
                plt.ylabel("Value")
            else: # Default to bar chart if type is unknown
                categories = ['Cat A', 'Cat B', 'Cat C']
                values = np.random.randint(20, 100, size=len(categories))
                sns.barplot(x=categories, y=values)

            plt.title(title)
            plt.tight_layout() # Adjust layout to prevent labels overlapping

            # Save the chart as a PNG image
            output_path = os.path.join(self.assets_dir, f"{slide_id}_chart.png")
            plt.savefig(output_path)
            plt.close() # Close the plot to free memory
            self.log(f"Placeholder chart saved successfully to {output_path}")
            return output_path
            
        except Exception as e:
            self.log(f"ERROR: Failed to generate placeholder chart. Details: {e}")
            plt.close() # Ensure plot is closed even if error occurs
            return None

    def _generate_diagram_from_dot(self, dot_code: str, slide_id: str) -> str | None:
        # ... (This function remains unchanged from diagram version)
        self.log(f"Attempting to generate diagram for slide {slide_id}...")
        try:
            source = graphviz.Source(dot_code)
            output_path = os.path.join(self.assets_dir, slide_id)
            rendered_path = source.render(output_path, format='png', cleanup=True)
            self.log(f"Diagram saved successfully to {rendered_path}")
            return rendered_path
        except graphviz.backend.execute.CalledProcessError as e:
            self.log(f"ERROR: Graphviz execution failed. Is Graphviz installed and in PATH? Error: {e}")
            return None
        except Exception as e:
            self.log(f"ERROR: Failed to generate diagram. Details: {e}")
            return None

    def _fetch_image_from_pexels(self, query: str, slide_id: str) -> str | None:
        # ... (This function remains unchanged from diagram version)
        if not self.pexels_api_key: return None
        headers = {"Authorization": self.pexels_api_key}
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data["photos"]:
                image_url = data["photos"][0]["src"]["medium"]
                image_response = requests.get(image_url, timeout=20)
                image_response.raise_for_status()
                file_extension = image_url.split('.')[-1].split('?')[0] or 'jpeg'
                file_path = os.path.join(self.assets_dir, f"{slide_id}.{file_extension}")
                with open(file_path, 'wb') as f: f.write(image_response.content)
                self.log(f"Image downloaded successfully to {file_path}")
                return file_path
        except requests.exceptions.RequestException as e:
            self.log(f"ERROR: Pexels API request failed. Details: {e}")
        return None

    def run(self):
        self.log("Starting visual asset generation (Charts > Diagrams > Photos)...")
        slides = self.sm.get("slides")
        if not slides: return

        for slide in slides:
            if slide.get("type") == "content":
                image_path = None
                
                # --- NEW LOGIC: Prioritize Charts, then Diagrams, then Photos ---
                chart_suggestion = slide.get("chart_suggestion")
                dot_code = slide.get("diagram_dot_code")
                image_hint = slide.get("image_hint")

                if chart_suggestion:
                    self.log(f"Found chart suggestion for slide {slide['id']}")
                    image_path = self._generate_placeholder_chart(chart_suggestion, slide["id"])
                
                if not image_path and dot_code:
                    self.log(f"No chart generated. Found diagram code for slide {slide['id']}")
                    image_path = self._generate_diagram_from_dot(dot_code, slide["id"])
                
                if not image_path and image_hint:
                    self.log(f"No chart or diagram. Searching Pexels for hint: '{image_hint}'")
                    image_path = self._fetch_image_from_pexels(image_hint, slide["id"])
                # -------------------------------------------------------------

                if image_path:
                    slide["image_path"] = image_path
            
        self.update_state("slides", slides)
        # self.sm.save("shared_state_after_media.json") # Keep commented unless debugging