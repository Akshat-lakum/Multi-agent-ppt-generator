# agents/content_agent.py
# ContentAgent updated to request speaker notes from the AI.

from .base_agent import BaseAgent
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# --- Function to split text into chunks (remains the same) ---
def chunk_text(text: str, chunk_size: int = 10000, overlap: int = 500) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
        if end >= len(text):
            break
    return chunks

class ContentAgent(BaseAgent):
    """
    Reads text from a PDF, chunks it, uses the Gemini API (requesting speaker notes),
    and combines the results to structure the content.
    """
    def __init__(self, name, state_manager, config=None):
        super().__init__(name, state_manager)
        load_dotenv()
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.log("Gemini API configured successfully.")
        except Exception as e:
            self.log(f"ERROR: Failed to configure Gemini API. Details: {e}")
        self.config = config or {}
        self.chunk_size = 12000
        self.overlap = 500

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        # ... (This function remains unchanged)
        if not os.path.exists(pdf_path):
            self.log(f"ERROR: PDF file not found at {pdf_path}")
            return ""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            self.log(f"Extracted {len(text)} characters from {pdf_path}")
            return text
        except Exception as e:
            self.log(f"ERROR: Failed to extract text from PDF. Details: {e}")
            return ""

    def _get_structured_content_from_llm(self, text_chunk: str, tone: str, slide_count: int) -> dict:
        """Sends a text chunk to the Gemini API, now requesting speaker notes."""
        if not text_chunk: return {}

        self.log(f"Sending chunk (length: {len(text_chunk)}) to Gemini API...")

        model = genai.GenerativeModel('models/gemini-2.5-pro')

        # --- UPDATED PROMPT ---
        prompt = f"""
        You are an expert educational content designer. Analyze the following text chunk from a syllabus and convert it into a structured JSON format for a presentation. Your output must be ONLY a well-formed JSON object.

        Specifications:
        1.  **Audience Tone**: Tailor for a '{tone}' audience.
        2.  **Output Format**: ONLY JSON with a top-level "chapters" key (list of chapter objects).
        3.  Each chapter: "id", "title", "description", "topics" list.
        4.  Each topic: "id", "title", "summary", "key_points", "quiz_questions", "image_hint".
        5.  **Speaker Notes**: For each topic, add a "speaker_notes" field containing a detailed script (2-4 sentences) that a presenter could read or use for talking points related to the slide's content.
        6.  **Diagrams**: If a topic describes a clear process/flow, include a "diagram_dot_code" field with simple Graphviz DOT code. Omit otherwise.

        Here is the text chunk:
        ---
        {text_chunk}
        ---
        """

        try:
            response = model.generate_content(prompt)
            if not response.parts:
                self.log("WARNING: Gemini API returned an empty response for this chunk.")
                return {}
            response_text = response.text.strip().lstrip('```json').rstrip('```')
            if not response_text:
                 self.log("WARNING: Gemini API returned empty text after stripping.")
                 return {}
            structured_data = json.loads(response_text)
            self.log("Successfully received and parsed structured content for chunk.")
            return structured_data
        except json.JSONDecodeError as e:
            self.log(f"ERROR: Failed to parse JSON from Gemini API response for chunk. Details: {e}")
            self.log(f"Raw response text: {response_text[:500]}...")
            return {}
        except Exception as e:
            self.log(f"ERROR: Failed to get structured content from Gemini API for chunk. Details: {e}")
            return {}

    def run(self):
        self.log("Starting real content extraction with chunking...")
        pdf_path = self.sm.get("input_pdf_path")
        tone = self.sm.get("tone") or "Beginner"
        slide_count = self.sm.get("slide_count") or 10

        if not pdf_path:
            self.log("ERROR: No input_pdf_path found. Aborting.")
            return

        full_text = self._extract_text_from_pdf(pdf_path)
        if not full_text: return

        text_chunks = chunk_text(full_text, chunk_size=self.chunk_size, overlap=self.overlap)
        self.log(f"Split text into {len(text_chunks)} chunks.")

        all_chapters = []
        for i, chunk in enumerate(text_chunks):
            self.log(f"Processing chunk {i+1}/{len(text_chunks)}...")
            structured_content = self._get_structured_content_from_llm(chunk, tone, slide_count)
            
            if structured_content and "chapters" in structured_content:
                all_chapters.extend(structured_content["chapters"])
            else:
                self.log(f"No valid 'chapters' structure returned for chunk {i+1}.")

        if all_chapters:
            self.update_state("chapters", all_chapters)
            self.log(f"Content processed from all chunks. Found {len(all_chapters)} chapters in total.")
            self.sm.save("shared_state_after_content.json")
        else:
            self.log("ERROR: No chapters were successfully processed from any chunk.")


























































































































































































































# # # agents/content_agent.py  (for initially dummy test)
# # # ContentAgent → generates structured content (chapters/topics).

# # from .base_agent import BaseAgent

# # class ContentAgent(BaseAgent):
# #     """
# #     Dummy ContentAgent: fills state with sample chapters/topics for testing.
# #     """
# #     def run(self):
# #         self.log("Starting dummy content extraction...")
        
# #         dummy_chapters = [
# #             {
# #                 "id": "ch1",
# #                 "title": "Chapter 1: Introduction",
# #                 "topics": [
# #                     {
# #                         "id": "t1",
# #                         "title": "Topic 1: Overview",
# #                         "summary": "This is a short summary of topic 1.",
# #                         "key_points": ["Point 1", "Point 2", "Point 3"]
# #                     },
# #                     {
# #                         "id": "t2",
# #                         "title": "Topic 2: Basics",
# #                         "summary": "Short summary of topic 2.",
# #                         "key_points": ["Point A", "Point B"]
# #                     }
# #                 ]
# #             },
# #             {
# #                 "id": "ch2",
# #                 "title": "Chapter 2: Advanced Concepts",
# #                 "topics": [
# #                     {
# #                         "id": "t3",
# #                         "title": "Topic 3: Deep Dive",
# #                         "summary": "Summary of topic 3.",
# #                         "key_points": ["Detail 1", "Detail 2"]
# #                     }
# #                 ]
# #             }
# #         ]

# #         self.update_state("chapters", dummy_chapters)
# #         self.log(f"Dummy chapters created: {len(dummy_chapters)}")


# # final dummy test 
# # agents/content_agent.py
# # Enhanced Dummy ContentAgent — produces richer, realistic-looking chapter/topic data
# from .base_agent import BaseAgent
# import uuid
# from datetime import datetime

# def _mkid(prefix="t"):
#     return f"{prefix}_{uuid.uuid4().hex[:8]}"

# class ContentAgent(BaseAgent):
#     """
#     Enhanced dummy ContentAgent for prototyping.
#     Produces multiple chapters with topics, summaries, key points, short examples,
#     short formulas, quiz questions, and image_hint keywords.
#     """

#     def __init__(self, name, state_manager, config=None):
#         super().__init__(name, state_manager)
#         self.config = config or {}

#     def run(self):
#         self.log("Starting enhanced dummy content extraction...")

#         # Create richer dummy chapters
#         chapters = []

#         # Chapter 1
#         chapters.append({
#             "id": "ch1",
#             "title": "Chapter 1: Introduction to Machine Learning",
#             "description": "Motivation, history, and key concepts of ML.",
#             "topics": [
#                 {
#                     "id": _mkid("t"),
#                     "title": "What is Machine Learning?",
#                     "summary": "Definition: Machine learning is a field of study that gives computers the ability to learn without being explicitly programmed. Focus on supervised, unsupervised and reinforcement learning.",
#                     "key_points": [
#                         "Definition and scope",
#                         "Difference from traditional programming",
#                         "Common tasks: classification, regression, clustering"
#                     ],
#                     "example": "Training a spam classifier using labeled emails.",
#                     "formula": "Loss(θ) = (1/n) Σ (y_i - f(x_i; θ))^2  (MSE)",
#                     "quiz_questions": [
#                         "What is the main difference between supervised and unsupervised learning?",
#                         "Give one example of a regression task."
#                     ],
#                     "image_hint": "illustration of supervised vs unsupervised learning"
#                 },
#                 {
#                     "id": _mkid("t"),
#                     "title": "Supervised Learning Basics",
#                     "summary": "Supervised learning uses labeled examples to learn a mapping from inputs to outputs.",
#                     "key_points": [
#                         "Training vs testing split",
#                         "Overfitting and underfitting",
#                         "Bias-variance tradeoff"
#                     ],
#                     "example": "Predicting house prices from features like size and location.",
#                     "formula": "ŷ = f(x; θ)",
#                     "quiz_questions": [
#                         "What is overfitting and how can it be mitigated?",
#                         "Why do we use a validation set?"
#                     ],
#                     "image_hint": "graph showing overfitting vs underfitting"
#                 }
#             ]
#         })

#         # Chapter 2
#         chapters.append({
#             "id": "ch2",
#             "title": "Chapter 2: Key Algorithms",
#             "description": "Overview of common ML algorithms and when to use them.",
#             "topics": [
#                 {
#                     "id": _mkid("t"),
#                     "title": "Linear Regression",
#                     "summary": "A method to model the relationship between a scalar response and one or more explanatory variables.",
#                     "key_points": [
#                         "Assumes linear relationship",
#                         "Ordinary least squares estimation",
#                         "Interpretation of coefficients"
#                     ],
#                     "example": "Predicting salary from years of experience using linear regression.",
#                     "formula": "β = (X^T X)^(-1) X^T y",
#                     "quiz_questions": [
#                         "Write the normal equation for linear regression.",
#                         "What assumptions does linear regression make about residuals?"
#                     ],
#                     "image_hint": "scatter plot with fitted regression line"
#                 },
#                 {
#                     "id": _mkid("t"),
#                     "title": "k-Nearest Neighbors (k-NN)",
#                     "summary": "A simple, non-parametric method used for classification and regression.",
#                     "key_points": [
#                         "Distance metric matters (e.g., Euclidean)",
#                         "Choice of k affects bias/variance",
#                         "No explicit training phase (lazy learner)"
#                     ],
#                     "example": "Classify iris species using nearest neighbors in feature space.",
#                     "formula": "distance(x, x') = sqrt(Σ (x_i - x'_i)^2)",
#                     "quiz_questions": [
#                         "How does increasing k affect the classifier?",
#                         "Name one situation where k-NN performs poorly."
#                     ],
#                     "image_hint": "k-nn decision boundary diagram"
#                 }
#             ]
#         })

#         # Chapter 3
#         chapters.append({
#             "id": "ch3",
#             "title": "Chapter 3: Model Evaluation & Good Practices",
#             "description": "Metrics, cross-validation, and practical tips for robust models.",
#             "topics": [
#                 {
#                     "id": _mkid("t"),
#                     "title": "Evaluation Metrics",
#                     "summary": "Common metrics include accuracy, precision, recall, F1-score for classification and RMSE for regression.",
#                     "key_points": [
#                         "Confusion matrix",
#                         "Precision vs recall tradeoff",
#                         "ROC curve and AUC"
#                     ],
#                     "example": "Use F1-score when classes are imbalanced.",
#                     "formula": "F1 = 2 * (precision * recall) / (precision + recall)",
#                     "quiz_questions": [
#                         "When should you prefer F1-score over accuracy?",
#                         "What does AUC measure?"
#                     ],
#                     "image_hint": "confusion matrix illustration"
#                 }
#             ]
#         })

#         # Save to shared state
#         self.update_state("chapters", chapters)
#         self.sm.append_log(f"ContentAgent: generated {len(chapters)} chapters (enhanced dummy)")
#         self.log(f"Enhanced dummy chapters created: {len(chapters)}")
#         # snapshot optional
#         try:
#             self.sm.save("shared_state_after_content.json")
#             self.log("Saved snapshot 'shared_state_after_content.json'")
#         except Exception:
#             pass
