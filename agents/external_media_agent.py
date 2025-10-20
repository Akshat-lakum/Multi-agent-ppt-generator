# agents/external_media_agent.py
# MediaAgent can now generate Mind Maps, Charts, Diagrams, or fetch photos.

from .base_agent import BaseAgent
from dotenv import load_dotenv
import os
import requests
import graphviz
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class ExternalMediaAgent(BaseAgent):
    """
    Chooses the best visual for a slide, prioritizing:
    1. Generates a Mind Map from DOT code.
    2. Generates a placeholder chart from AI suggestion.
    3. Generates a diagram from DOT code.
    4. Fetches a stock photo from Pexels.
    """
    def __init__(self, name, state_manager, config=None):
        # ... (init remains the same)
        super().__init__(name, state_manager)
        load_dotenv()
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.assets_dir = "assets"
        os.makedirs(self.assets_dir, exist_ok=True)
        sns.set_theme(style="whitegrid")

    def _generate_mind_map_from_dot(self, dot_code: str, slide_id: str) -> str | None:
        """Renders Graphviz DOT code into a PNG image suitable for a mind map."""
        self.log(f"Attempting to generate mind map for slide {slide_id}...")
        try:
            # Use 'neato' or 'fdp' layout engines which are often better for mind maps
            # Wrap dot_code in graph {} if it's not already
            if not dot_code.strip().lower().startswith("graph"):
                 dot_code = f"graph G {{ layout=neato; overlap=scale; {dot_code} }}"
            else:
                 # Inject layout engine if graph {} exists but no layout specified
                 if 'layout=' not in dot_code:
                      dot_code = dot_code.replace('{', '{ layout=neato; overlap=scale; ', 1)


            source = graphviz.Source(dot_code)
            output_path = os.path.join(self.assets_dir, f"{slide_id}_mindmap") # Distinct name
            rendered_path = source.render(output_path, format='png', cleanup=True)
            self.log(f"Mind map saved successfully to {rendered_path}")
            return rendered_path
        except graphviz.backend.execute.CalledProcessError as e:
            self.log(f"ERROR: Graphviz execution failed for mind map. Is Graphviz installed/PATH ok? Error: {e}")
            return None
        except Exception as e:
            self.log(f"ERROR: Failed to generate mind map. Details: {e}")
            return None

    def _generate_placeholder_chart(self, suggestion: dict, slide_id: str) -> str | None:
        # ... (This function remains unchanged)
        chart_type = suggestion.get("type", "bar")
        title = suggestion.get("title", "Placeholder Chart")
        self.log(f"Generating placeholder '{chart_type}' chart for slide {slide_id}: '{title}'")
        try:
            plt.figure(figsize=(8, 4))
            if chart_type == "bar":
                categories = ['Category A', 'Category B', 'Category C', 'Category D']
                values = np.random.randint(20, 100, size=len(categories))
                sns.barplot(x=categories, y=values, palette="viridis")
            elif chart_type == "line":
                x_values = np.arange(1, 11); y_values = np.random.rand(10) * 50 + 50
                sns.lineplot(x=x_values, y=y_values, marker='o'); plt.xlabel("Time/Sequence"); plt.ylabel("Value")
            else:
                categories = ['Cat A', 'Cat B', 'Cat C']; values = np.random.randint(20, 100, size=len(categories))
                sns.barplot(x=categories, y=values)
            plt.title(title); plt.tight_layout()
            output_path = os.path.join(self.assets_dir, f"{slide_id}_chart.png")
            plt.savefig(output_path); plt.close()
            self.log(f"Placeholder chart saved successfully to {output_path}")
            return output_path
        except Exception as e:
            self.log(f"ERROR: Failed to generate placeholder chart. Details: {e}"); plt.close(); return None


    def _generate_diagram_from_dot(self, dot_code: str, slide_id: str) -> str | None:
        # ... (This function remains unchanged)
        self.log(f"Attempting to generate diagram for slide {slide_id}...")
        try:
            # Ensure it's treated as a directed graph
            if not dot_code.strip().lower().startswith("digraph"):
                 dot_code = f"digraph G {{ {dot_code} }}"
            source = graphviz.Source(dot_code)
            output_path = os.path.join(self.assets_dir, f"{slide_id}_diagram") # Distinct name
            rendered_path = source.render(output_path, format='png', cleanup=True)
            self.log(f"Diagram saved successfully to {rendered_path}")
            return rendered_path
        except graphviz.backend.execute.CalledProcessError as e:
            self.log(f"ERROR: Graphviz execution failed for diagram. Error: {e}"); return None
        except Exception as e:
            self.log(f"ERROR: Failed to generate diagram. Details: {e}"); return None

    def _fetch_image_from_pexels(self, query: str, slide_id: str) -> str | None:
        # ... (This function remains unchanged)
        if not self.pexels_api_key: return None
        headers = {"Authorization": self.pexels_api_key}
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
        try:
            response = requests.get(url, headers=headers); response.raise_for_status()
            data = response.json()
            if data["photos"]:
                image_url = data["photos"][0]["src"]["medium"]
                image_response = requests.get(image_url, timeout=20); image_response.raise_for_status()
                file_extension = image_url.split('.')[-1].split('?')[0] or 'jpeg'
                file_path = os.path.join(self.assets_dir, f"{slide_id}_photo.{file_extension}") # Add type to name
                with open(file_path, 'wb') as f: f.write(image_response.content)
                self.log(f"Image downloaded successfully to {file_path}")
                return file_path
        except requests.exceptions.RequestException as e:
            self.log(f"ERROR: Pexels API request failed. Details: {e}")
        return None

    def run(self):
        self.log("Starting visual asset generation (Mind Maps > Charts > Diagrams > Photos)...")
        slides = self.sm.get("slides")
        if not slides: return

        for slide in slides:
            if slide.get("type") == "content":
                image_path = None
                
                # --- NEW PRIORITIZED LOGIC ---
                mind_map_code = slide.get("mind_map_dot_code")
                chart_suggestion = slide.get("chart_suggestion")
                diagram_code = slide.get("diagram_dot_code")
                image_hint = slide.get("image_hint")

                if mind_map_code:
                    self.log(f"Found Mind Map code for slide {slide['id']}")
                    image_path = self._generate_mind_map_from_dot(mind_map_code, slide["id"])

                if not image_path and chart_suggestion:
                    self.log(f"No mind map. Found chart suggestion for slide {slide['id']}")
                    image_path = self._generate_placeholder_chart(chart_suggestion, slide["id"])
                
                if not image_path and diagram_code:
                    self.log(f"No mind map or chart. Found diagram code for slide {slide['id']}")
                    image_path = self._generate_diagram_from_dot(diagram_code, slide["id"])
                
                if not image_path and image_hint:
                    self.log(f"No mind map, chart, or diagram. Searching Pexels for hint: '{image_hint}'")
                    image_path = self._fetch_image_from_pexels(image_hint, slide["id"])
                # --------------------------------

                if image_path:
                    slide["image_path"] = image_path
            
        self.update_state("slides", slides)