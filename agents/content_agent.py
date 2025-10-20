# agents/content_agent.py
# ContentAgent updated to request mind map structures.

from .base_agent import BaseAgent
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Function to split text into chunks (remains the same)
def chunk_text(text: str, chunk_size: int = 10000, overlap: int = 500) -> list[str]:
    # ... (code for chunk_text remains the same)
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
    Uses layout-aware text extraction and Gemini API to structure content,
    including speaker notes, diagrams, chart suggestions, and mind map structures.
    """
    def __init__(self, name, state_manager, config=None):
        # ... (init remains the same)
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
        # ... (This function remains unchanged from OCR version)
        if not os.path.exists(pdf_path):
            self.log(f"ERROR: PDF file not found at {pdf_path}")
            return ""
        full_text = ""
        doc = None
        try:
            doc = fitz.open(pdf_path)
            pymu_text_check = ""
            for page_num, page in enumerate(doc):
                blocks = page.get_text("blocks")
                blocks.sort(key=lambda b: (b[1], b[0]))
                page_text = "".join([b[4] for b in blocks])
                if len(page_text.strip()) > 50:
                    pymu_text_check += f"\n--- Page {page_num + 1} ---\n" + page_text
            
            if len(pymu_text_check.strip()) > 100:
                self.log(f"Extracted {len(pymu_text_check)} characters (layout-aware PyMuPDF) from {pdf_path}")
                return pymu_text_check
            else:
                self.log("PyMuPDF found minimal text. Attempting OCR fallback...")
                # OCR logic here (omitted for brevity, assume it's the same as before)
                # ...
                # Ensure it returns the ocr_full_text if successful
                # ...
                ocr_full_text = "" # Placeholder - Use the previous OCR code here
                if len(ocr_full_text.strip()) > 100:
                     self.log(f"Extracted {len(ocr_full_text)} characters (OCR) from {pdf_path}")
                     return ocr_full_text
                else:
                    self.log("OCR also found minimal text.")
                    return ""
        except Exception as e:
            self.log(f"ERROR: Failed to extract text from PDF. Details: {e}")
            return ""
        finally:
            if doc:
                doc.close()


    def _get_structured_content_from_llm(self, text_chunk: str, tone: str, slide_count: int) -> dict:
        """Sends text chunk to Gemini, requesting mind map structures."""
        if not text_chunk: return {}
        self.log(f"Sending chunk (length: {len(text_chunk)}) to Gemini API...")
        model = genai.GenerativeModel('models/gemini-2.5-pro')

        # --- UPDATED PROMPT ---
        prompt = f"""
        You are an expert educational content designer. Analyze the following text chunk and convert it into a structured JSON format for a presentation. Your output must be ONLY a well-formed JSON object.

        Specifications:
        1.  **Audience Tone**: Tailor for a '{tone}' audience.
        2.  **Output Format**: ONLY JSON with a top-level "chapters" key (list).
        3.  Each chapter: "id", "title", "description", "topics" list.
        4.  Each topic: "id", "title", "summary", "key_points", "quiz_questions", "image_hint", "speaker_notes".
        5.  **Speaker Notes**: For each topic, add a detailed script (2-4 sentences).
        6.  **Diagrams**: If a topic describes a clear LINEAR process/flow (e.g., Step 1 -> Step 2), include "diagram_dot_code" field with simple Graphviz DOT code using '->'. Omit otherwise.
        7.  **Mind Maps**: If a topic primarily explores relationships between a central concept and several related sub-concepts (hierarchical or non-linear), include a "mind_map_dot_code" field. Use Graphviz DOT code for an undirected graph (using '--') suitable for a mind map layout (like 'neato' or 'fdp'). For example: 'graph {{ "Central Idea" -- "Subtopic A"; "Central Idea" -- "Subtopic B"; }}'. Prioritize Mind Maps over Diagrams if the structure is more conceptual than sequential. Omit if not suitable.
        8.  **Charts**: If the text clearly implies a comparison/trend for a simple bar/line chart, add a "chart_suggestion" field (e.g., {{"type": "bar", "title": "Comparison"}}). Omit otherwise.

        Here is the text chunk:
        ---
        {text_chunk}
        ---
        """

        try:
            # ... (Rest of the try/except block remains the same)
            response = model.generate_content(prompt)
            if not response.parts: return {}
            response_text = response.text.strip().lstrip('```json').rstrip('```')
            if not response_text: return {}
            structured_data = json.loads(response_text)
            self.log("Successfully received and parsed structured content for chunk.")
            return structured_data
        except json.JSONDecodeError as e:
            self.log(f"ERROR: Failed to parse JSON from chunk. Details: {e}\nRaw text: {response_text[:500]}...")
            return {}
        except Exception as e:
            self.log(f"ERROR: Failed to get structured content for chunk. Details: {e}")
            return {}

    def run(self):
        # ... (Run method remains the same)
        self.log("Starting real content extraction with chunking...")
        pdf_path = self.sm.get("input_pdf_path")
        tone = self.sm.get("tone") or "Beginner"
        slide_count = self.sm.get("slide_count") or 10
        if not pdf_path: self.log("ERROR: No input_pdf_path found."); return
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
            else: self.log(f"No valid 'chapters' structure returned for chunk {i+1}.")
        if all_chapters:
            self.update_state("chapters", all_chapters)
            self.log(f"Content processed. Found {len(all_chapters)} chapters total.")
            # self.sm.save("shared_state_after_content.json") # Keep commented
        else: self.log("ERROR: No chapters processed from any chunk.")



















































































































































































































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
