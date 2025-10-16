# agents/external_media_agent.py
# The MediaAgent can now generate diagrams with Graphviz or fetch photos from Pexels.

from .base_agent import BaseAgent
from dotenv import load_dotenv
import os
import requests
import graphviz # Import the new library

class ExternalMediaAgent(BaseAgent):
    """
    Chooses the best visual for a slide:
    1.  Generates a diagram from DOT code if available.
    2.  Falls back to fetching a stock photo from Pexels using an image hint.
    """

    def __init__(self, name, state_manager, config=None):
        super().__init__(name, state_manager)
        load_dotenv()
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        if not self.pexels_api_key:
            self.log("WARNING: PEXELS_API_KEY not found. Stock photo search will be disabled.")
        self.assets_dir = "assets"
        os.makedirs(self.assets_dir, exist_ok=True)

    def _generate_diagram_from_dot(self, dot_code: str, slide_id: str) -> str | None:
        """Renders Graphviz DOT code into a PNG image."""
        self.log(f"Generating diagram for slide {slide_id}...")
        try:
            # Create a source object from the DOT code
            source = graphviz.Source(dot_code)
            # Define the output path without the .png extension
            output_path = os.path.join(self.assets_dir, slide_id)
            # Render the diagram, which saves it as output_path.png
            rendered_path = source.render(output_path, format='png', cleanup=True)
            self.log(f"Diagram saved successfully to {rendered_path}")
            return rendered_path
        except Exception as e:
            self.log(f"ERROR: Failed to generate diagram with Graphviz. Details: {e}")
            return None

    def _fetch_image_from_pexels(self, query: str, slide_id: str) -> str | None:
        """Searches Pexels, downloads an image, and returns its path."""
        if not self.pexels_api_key: return None
        
        headers = {"Authorization": self.pexels_api_key}
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
        try:
            # Search for the image URL
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data["photos"]:
                image_url = data["photos"][0]["src"]["medium"]
                # Download the image
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                
                file_path = os.path.join(self.assets_dir, f"{slide_id}.jpeg")
                with open(file_path, 'wb') as f:
                    f.write(image_response.content)
                self.log(f"Image downloaded successfully to {file_path}")
                return file_path
        except requests.exceptions.RequestException as e:
            self.log(f"ERROR: Pexels API request failed. Details: {e}")
        return None

    def run(self):
        self.log("Starting visual asset generation...")
        slides = self.sm.get("slides")
        if not slides: return

        for slide in slides:
            if slide.get("type") == "content":
                image_path = None
                # --- NEW LOGIC: Prioritize diagrams ---
                if slide.get("diagram_dot_code"):
                    image_path = self._generate_diagram_from_dot(slide["diagram_dot_code"], slide["id"])
                
                # If no diagram was created, fall back to Pexels
                if not image_path and slide.get("image_hint"):
                    self.log(f"No diagram code found. Searching Pexels for hint: '{slide['image_hint']}'")
                    image_path = self._fetch_image_from_pexels(slide["image_hint"], slide["id"])

                if image_path:
                    slide["image_path"] = image_path
        
        self.update_state("slides", slides)
        self.sm.save("shared_state_after_media.json")
        