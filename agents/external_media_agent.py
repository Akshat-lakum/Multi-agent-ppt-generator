# agents/external_media_agent.py
# MediaAgent can now generate REAL charts from data, diagrams, mind maps, or fetch photos.

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
    2. Generates a real chart from provided data.
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
        # ... (This function remains unchanged)
        self.log(f"Attempting to generate mind map for slide {slide_id}...")
        try:
            if not dot_code.strip().lower().startswith("graph"): dot_code = f"graph G {{ layout=neato; overlap=scale; {dot_code} }}"
            else:
                 if 'layout=' not in dot_code: dot_code = dot_code.replace('{', '{ layout=neato; overlap=scale; ', 1)
            source = graphviz.Source(dot_code)
            output_path = os.path.join(self.assets_dir, f"{slide_id}_mindmap")
            rendered_path = source.render(output_path, format='png', cleanup=True)
            self.log(f"Mind map saved successfully to {rendered_path}"); return rendered_path
        except graphviz.backend.execute.CalledProcessError as e: self.log(f"ERROR: Graphviz failed for mind map. {e}"); return None
        except Exception as e: self.log(f"ERROR: Failed to generate mind map. {e}"); return None

    # --- UPDATED: Generates chart from actual data provided by AI ---
    def _generate_real_chart(self, suggestion: dict, data: dict, slide_id: str) -> str | None:
        """Generates a chart image based on AI suggestion AND extracted data."""
        chart_type = suggestion.get("type", "bar")
        title = suggestion.get("title", "Chart")
        labels = data.get("labels")
        values = data.get("values")

        # Basic validation
        if not labels or not values or len(labels) != len(values):
            self.log(f"ERROR: Invalid or mismatched chart data for slide {slide_id}. Labels: {labels}, Values: {values}")
            return None
        # Ensure values are numeric
        try:
             numeric_values = [float(v) for v in values]
        except (ValueError, TypeError):
             self.log(f"ERROR: Chart values are not numeric for slide {slide_id}. Values: {values}")
             return None

        self.log(f"Generating '{chart_type}' chart for slide {slide_id}: '{title}' using provided data.")

        try:
            plt.figure(figsize=(8, 4.5)) # Adjusted size slightly

            if chart_type == "bar":
                sns.barplot(x=labels, y=numeric_values, palette="viridis")
                plt.xticks(rotation=45, ha='right') # Rotate labels if they overlap
            elif chart_type == "line":
                sns.lineplot(x=labels, y=numeric_values, marker='o')
                plt.xticks(rotation=45, ha='right')
                # Assuming labels might be time/sequence if it's a line chart
                # plt.xlabel("Category/Time")
                plt.ylabel("Value")
            else: # Default to bar
                sns.barplot(x=labels, y=numeric_values)
                plt.xticks(rotation=45, ha='right')

            plt.title(title)
            plt.tight_layout()

            output_path = os.path.join(self.assets_dir, f"{slide_id}_chart.png")
            plt.savefig(output_path)
            plt.close()
            self.log(f"Chart saved successfully to {output_path}")
            return output_path

        except Exception as e:
            self.log(f"ERROR: Failed to generate real chart. Details: {e}")
            plt.close()
            return None
    # -------------------------------------------------------------------

    def _generate_diagram_from_dot(self, dot_code: str, slide_id: str) -> str | None:
        # ... (This function remains unchanged)
        self.log(f"Attempting to generate diagram for slide {slide_id}...")
        try:
            if not dot_code.strip().lower().startswith("digraph"): dot_code = f"digraph G {{ {dot_code} }}"
            source = graphviz.Source(dot_code)
            output_path = os.path.join(self.assets_dir, f"{slide_id}_diagram")
            rendered_path = source.render(output_path, format='png', cleanup=True)
            self.log(f"Diagram saved successfully to {rendered_path}"); return rendered_path
        except graphviz.backend.execute.CalledProcessError as e: self.log(f"ERROR: Graphviz failed for diagram. {e}"); return None
        except Exception as e: self.log(f"ERROR: Failed to generate diagram. {e}"); return None

    def _fetch_image_from_pexels(self, query: str, slide_id: str) -> str | None:
        # ... (This function remains unchanged)
        if not self.pexels_api_key: return None
        headers = {"Authorization": self.pexels_api_key}; url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
        try:
            response = requests.get(url, headers=headers); response.raise_for_status(); data = response.json()
            if data["photos"]:
                image_url = data["photos"][0]["src"]["medium"]
                image_response = requests.get(image_url, timeout=20); image_response.raise_for_status()
                file_extension = image_url.split('.')[-1].split('?')[0] or 'jpeg'
                file_path = os.path.join(self.assets_dir, f"{slide_id}_photo.{file_extension}")
                with open(file_path, 'wb') as f: f.write(image_response.content)
                self.log(f"Image downloaded successfully to {file_path}"); return file_path
        except requests.exceptions.RequestException as e: self.log(f"ERROR: Pexels API request failed. {e}")
        return None

    # --- UPDATED: Run method includes real chart generation ---
    def run(self):
        self.log("Starting visual asset generation (Mind Maps > Charts > Diagrams > Photos)...")
        slides = self.sm.get("slides")
        if not slides: return

        for slide in slides:
            if slide.get("type") == "content":
                image_path = None
                
                # Check for all potential visual types in order of priority
                mind_map_code = slide.get("mind_map_dot_code")
                chart_suggestion = slide.get("chart_suggestion")
                chart_data = slide.get("chart_data") # Get the chart data
                diagram_code = slide.get("diagram_dot_code")
                image_hint = slide.get("image_hint")

                if mind_map_code:
                    self.log(f"Found Mind Map code for slide {slide['id']}")
                    image_path = self._generate_mind_map_from_dot(mind_map_code, slide["id"])

                # Generate real chart if suggestion AND data are present
                elif chart_suggestion and chart_data:
                    self.log(f"Found chart suggestion and data for slide {slide['id']}")
                    image_path = self._generate_real_chart(chart_suggestion, chart_data, slide["id"])
                
                elif diagram_code:
                    self.log(f"No mind map or chart. Found diagram code for slide {slide['id']}")
                    image_path = self._generate_diagram_from_dot(diagram_code, slide["id"])
                
                elif image_hint:
                    self.log(f"No mind map, chart, or diagram. Searching Pexels for hint: '{image_hint}'")
                    image_path = self._fetch_image_from_pexels(image_hint, slide["id"])

                if image_path:
                    slide["image_path"] = image_path
            
        self.update_state("slides", slides)