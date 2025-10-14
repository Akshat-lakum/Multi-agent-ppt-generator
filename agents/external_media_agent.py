# agents/external_media_agent.py
# New Agent: Fetches images from the web based on image_hints.

from .base_agent import BaseAgent
from dotenv import load_dotenv
import os
import requests

class ExternalMediaAgent(BaseAgent):
    """
    Searches for and downloads images based on hints provided by the ContentAgent.
    """

    def __init__(self, name, state_manager, config=None):
        super().__init__(name, state_manager)
        load_dotenv()
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        if not self.pexels_api_key:
            self.log("ERROR: PEXELS_API_KEY not found in .env file.")
        self.assets_dir = "assets"
        os.makedirs(self.assets_dir, exist_ok=True)

    def _fetch_image_url(self, query: str) -> str | None:
        """Searches Pexels for an image and returns its URL."""
        if not self.pexels_api_key:
            return None
        
        headers = {"Authorization": self.pexels_api_key}
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status() # Raises an exception for bad status codes
            data = response.json()
            if data["photos"]:
                # Get a medium-sized photo URL
                return data["photos"][0]["src"]["medium"]
        except requests.exceptions.RequestException as e:
            self.log(f"ERROR: Pexels API request failed. Details: {e}")
        return None

    def _download_image(self, url: str, slide_id: str) -> str | None:
        """Downloads an image from a URL and saves it to the assets folder."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Use the slide_id to create a unique filename
            file_extension = url.split('.')[-1].split('?')[0]
            if not file_extension: file_extension = 'jpg'
            file_path = os.path.join(self.assets_dir, f"{slide_id}.{file_extension}")
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            self.log(f"Image downloaded successfully to {file_path}")
            return file_path
        except requests.exceptions.RequestException as e:
            self.log(f"ERROR: Failed to download image. Details: {e}")
        return None

    def run(self):
        self.log("Starting media fetching...")
        slides = self.sm.get("slides")
        if not slides:
            self.log("No slides found to add media to.")
            return

        for slide in slides:
            if slide.get("type") == "content" and slide.get("image_hint"):
                hint = slide["image_hint"]
                self.log(f"Searching for image with hint: '{hint}'")
                
                image_url = self._fetch_image_url(hint)
                if image_url:
                    image_path = self._download_image(image_url, slide["id"])
                    if image_path:
                        # Add the local path to the slide data
                        slide["image_path"] = image_path
        
        # Update the state with the modified slides list
        self.update_state("slides", slides)
        self.sm.save("shared_state_after_media.json")