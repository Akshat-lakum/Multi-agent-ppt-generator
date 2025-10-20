# agents/qa_agent.py
# New Agent: Evaluates the quality of the generated slides using an LLM.

from .base_agent import BaseAgent
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

class QAAgent(BaseAgent):
    """
    Uses an LLM (Gemini) to review the generated slide content for quality,
    accuracy (based on summary/title), and relevance.
    """
    def __init__(self, name, state_manager, config=None):
        super().__init__(name, state_manager)
        load_dotenv()
        try:
            # Re-configure Gemini API if needed, or assume it's configured by ContentAgent
            # It's safer to configure it here too.
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.log("Gemini API configured for QA.")
        except Exception as e:
            self.log(f"ERROR: Failed to configure Gemini API for QA. Details: {e}")
        self.config = config or {}

    def _prepare_evaluation_prompt(self, slides_data: list) -> str:
        """Creates a prompt for the LLM to evaluate the slides."""
        
        # Prepare a simplified text representation of the slides for the LLM
        slides_text_for_eval = ""
        for i, slide in enumerate(slides_data):
            slide_type = slide.get("type", "content")
            title = slide.get("title", f"Slide {i+1}")
            summary = ""
            if slide_type == "content":
                summary = slide.get("summary", "") # Assuming summary exists, adjust if needed based on ContentAgent output
            elif slide_type == "quiz":
                 summary = "Quiz questions slide." # Simple description for quiz
            
            image_hint = slide.get("image_hint", "N/A")
            
            slides_text_for_eval += f"Slide {i+1} (Type: {slide_type}):\n"
            slides_text_for_eval += f"  Title: {title}\n"
            if summary:
                 slides_text_for_eval += f"  Summary/Content: {summary}\n"
            slides_text_for_eval += f"  Image Hint: {image_hint}\n---\n"

        prompt = f"""
        You are an expert educational content reviewer. Please evaluate the following slide plan based on the provided titles, summaries, and image hints.

        Evaluation Criteria:
        1.  **Clarity & Conciseness**: Is the title and summary clear and easy to understand for the likely topic?
        2.  **Likely Accuracy**: Does the summary seem plausible and relevant given the title? (You don't have the original source, but make an educated guess).
        3.  **Image Hint Relevance**: Does the 'Image Hint' seem relevant to the slide's title and summary?
        4.  **Overall Flow**: Does the sequence of slides seem logical?

        Provide your feedback as a brief overall summary (2-3 sentences) followed by a list of specific observations or suggestions for improvement (if any). Focus on potential issues.

        Slide Plan for Review:
        ---
        {slides_text_for_eval[:15000]} 
        ---

        Your Evaluation:
        """
        return prompt

    def _get_qa_feedback_from_llm(self, prompt: str) -> str:
        """Sends the evaluation prompt to Gemini and gets feedback."""
        if not os.getenv("GEMINI_API_KEY"):
             return "QA Skipped: Gemini API key not configured."

        self.log("Sending slide plan to Gemini for QA evaluation...")
        model = genai.GenerativeModel('models/gemini-2.5-pro') # Or your preferred model

        try:
            response = model.generate_content(prompt)
            if not response.parts:
                self.log("WARNING: Gemini API returned an empty QA response.")
                return "QA Failed: Empty response from AI."
            feedback = response.text
            self.log("Successfully received QA feedback from Gemini.")
            return feedback
        except Exception as e:
            self.log(f"ERROR: Failed to get QA feedback from Gemini. Details: {e}")
            return f"QA Failed: {e}"

    def run(self):
        self.log("Starting QA evaluation of generated slides...")
        
        slides = self.sm.get("slides")
        if not slides:
            self.log("ERROR: No slides found in state to evaluate. Aborting QA.")
            return

        # Prepare the prompt with the slide data
        evaluation_prompt = self._prepare_evaluation_prompt(slides)
        
        # Get feedback from the LLM
        qa_feedback = self._get_qa_feedback_from_llm(evaluation_prompt)
        
        # Add the feedback to the shared state
        self.update_state("qa_feedback", qa_feedback)
        self.log("QA evaluation complete.")
        # Optionally print feedback to console
        print("\n--- AI Quality Assurance Feedback ---")
        print(qa_feedback)
        print("------------------------------------\n")
        
        # Save state if needed (optional for QA)
        # self.sm.save("shared_state_after_qa.json")