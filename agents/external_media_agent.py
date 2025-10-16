# agents/external_media_agent.py
# Final Agent: Generates custom images using the free Stable Diffusion model via Replicate.

from .base_agent import BaseAgent
from dotenv import load_dotenv
import os
import requests
import replicate # Import the new library

class ExternalMediaAgent(BaseAgent):
    """
    Generates and downloads custom images using Stable Diffusion via the Replicate API,
    based on hints provided by the ContentAgent.
    """

    def __init__(self, name, state_manager, config=None):
        super().__init__(name, state_manager)
        load_dotenv()
        # Set the Replicate API token
        self.replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
        if not self.replicate_api_token:
            self.log("ERROR: REPLICATE_API_TOKEN not found in .env file.")
        # Replicate library automatically uses the environment variable, but good to check
        
        self.assets_dir = "assets"
        os.makedirs(self.assets_dir, exist_ok=True)

    def _generate_image_with_sd(self, hint: str) -> str | None:
        """Generates an image using Stable Diffusion and returns its URL."""
        if not self.replicate_api_token:
            return None
        
        # A descriptive prompt for better results with Stable Diffusion
        sd_prompt = f"A clear, simple, minimalist educational diagram illustrating the concept of: '{hint}'. White background, infographic style, high quality."
        self.log(f"Sending prompt to Stable Diffusion: '{sd_prompt}'")
        
        try:
            # This is the identifier for the Stable Diffusion 3 model on Replicate
            model_identifier = "stability-ai/stable-diffusion-3"
            
            output = replicate.run(
                model_identifier,
                input={"prompt": sd_prompt}
            )
            # The output is a list of URLs, we'll take the first one
            image_url = output[0]
            return image_url
        except Exception as e:
            self.log(f"ERROR: Replicate API request failed. Details: {e}")
            return None

    def _download_image(self, url: str, slide_id: str) -> str | None:
        """Downloads an image from a URL and saves it to the assets folder."""
        try:
            response = requests.get(url, timeout=20) # Add a timeout
            response.raise_for_status()
            
            # Stable Diffusion generates PNGs
            file_path = os.path.join(self.assets_dir, f"{slide_id}.png")
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            self.log(f"Image downloaded successfully to {file_path}")
            return file_path
        except requests.exceptions.RequestException as e:
            self.log(f"ERROR: Failed to download image. Details: {e}")
        return None

    def run(self):
        self.log("Starting AI image generation with Stable Diffusion...")
        slides = self.sm.get("slides")
        if not slides:
            self.log("No slides found to add media to.")
            return

        for slide in slides:
            if slide.get("type") == "content" and slide.get("image_hint"):
                hint = slide["image_hint"]
                
                # Call the new Stable Diffusion function
                image_url = self._generate_image_with_sd(hint)
                
                if image_url:
                    image_path = self._download_image(image_url, slide["id"])
                    if image_path:
                        slide["image_path"] = image_path
        
        self.update_state("slides", slides)
        self.sm.save("shared_state_after_media.json")