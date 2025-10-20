# agents/content_agent.py
# ContentAgent updated to include table data in prompts and request chart data extraction.

from .base_agent import BaseAgent
import fitz # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import pytesseract
from PIL import Image
import io
import camelot
import pandas as pd

# Function to split text into chunks (remains the same)
def chunk_text(text: str, chunk_size: int = 10000, overlap: int = 500) -> list[str]:
    # ... (code remains the same)
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
    Extracts text and tables, includes table representations in prompts,
    and asks Gemini to extract chart data alongside other content structures.
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

    def _extract_text_and_tables_from_pdf(self, pdf_path: str) -> tuple[str, list[pd.DataFrame]]:
        # ... (This function remains the same as the Camelot version)
        # ... (It extracts text using PyMuPDF+OCR and tables using Camelot) ...
        # ... (It should return: full_text_string, list_of_table_dataframes) ...
        if not os.path.exists(pdf_path): return "", []
        full_text = ""
        extracted_tables = []
        doc = None
        try:
            # (PyMuPDF + OCR logic here)
            doc = fitz.open(pdf_path); pymu_text_check = ""
            for page_num, page in enumerate(doc):
                blocks = page.get_text("blocks"); blocks.sort(key=lambda b: (b[1], b[0]))
                page_text = "".join([b[4] for b in blocks])
                if len(page_text.strip()) > 50: pymu_text_check += f"\n--- Page {page_num + 1} ---\n" + page_text
            if len(pymu_text_check.strip()) > 100: full_text = pymu_text_check; self.log(f"Extracted {len(full_text)} chars (PyMuPDF)")
            else:
                self.log("PyMuPDF found minimal text. Attempting OCR...")
                ocr_full_text = ""
                # (OCR logic here)
                for page_num, page in enumerate(doc):
                     pix = page.get_pixmap(); img = Image.open(io.BytesIO(pix.pil_tobytes("png")))
                     try: page_ocr_text = pytesseract.image_to_string(img, lang='eng'); ocr_full_text += f"\n--- OCR Page {page_num + 1} ---\n" + page_ocr_text
                     except pytesseract.TesseractNotFoundError: self.log("ERROR: Tesseract OCR not found."); return "", []
                     except Exception as ocr_e: self.log(f"ERROR: OCR failed page {page_num+1}. {ocr_e}")
                if len(ocr_full_text.strip()) > 100: full_text = ocr_full_text; self.log(f"Extracted {len(full_text)} chars (OCR)")
                else: self.log("OCR also found minimal text."); full_text = ""

            # (Camelot Table Extraction logic here)
            self.log("Attempting table extraction with Camelot...")
            tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice', suppress_stdout=True)
            if tables:
                self.log(f"Camelot found {tables.n} potential tables.")
                for i, table in enumerate(tables):
                    self.log(f"--- Table {i+1} (Page {table.page}) ---")
                    print(table.df.head().to_string())
                    extracted_tables.append(table.df)
            else: self.log("Camelot found no tables.")
        except ImportError: self.log("WARNING: Camelot library missing. Skipping table extraction.")
        except Exception as e: self.log(f"ERROR during text/table extraction: {e}")
        finally:
             if doc: doc.close()
        return full_text, extracted_tables


    # --- UPDATED: Includes table text in prompt, asks for chart_data ---
    def _get_structured_content_from_llm(self, text_chunk: str, tables_in_chunk: list[str], tone: str, slide_count: int) -> dict:
        """Sends text chunk (potentially with table data) to Gemini, requesting chart data extraction."""
        if not text_chunk and not tables_in_chunk: return {}

        self.log(f"Sending chunk (length: {len(text_chunk)}) to Gemini API...")
        model = genai.GenerativeModel('models/gemini-2.5-pro')

        # Combine text and table representations for the prompt
        prompt_content = text_chunk
        if tables_in_chunk:
            prompt_content += "\n\n--- Extracted Tables in this Section ---\n"
            for i, table_md in enumerate(tables_in_chunk):
                prompt_content += f"\nTable {i+1}:\n{table_md}\n"
            prompt_content += "--- End of Extracted Tables ---\n"

        prompt = f"""
        You are an expert educational content designer. Analyze the following text chunk (which might include text representations of tables) from a syllabus and convert it into a structured JSON format for a presentation. Your output must be ONLY a well-formed JSON object.

        Specifications:
        1.  **Audience Tone**: Tailor for a '{tone}' audience.
        2.  **Output Format**: ONLY JSON with a top-level "chapters" key (list).
        3.  Each chapter: "id", "title", "description", "topics" list.
        4.  Each topic: "id", "title", "summary", "key_points", "quiz_questions", "image_hint", "speaker_notes".
        5.  **Speaker Notes**: For each topic, add a detailed script (2-4 sentences).
        6.  **Diagrams**: If a topic describes a clear LINEAR process/flow, include "diagram_dot_code" field with simple Graphviz DOT code. Omit otherwise.
        7.  **Mind Maps**: If a topic explores relationships (hierarchical/non-linear), include "mind_map_dot_code" field with undirected Graphviz DOT code. Prioritize Mind Maps over Diagrams if conceptual. Omit otherwise.
        8.  **Charts**: If the text or included table data clearly represents information suitable for a simple bar or line chart (e.g., comparison, trend), add BOTH:
            * `"chart_suggestion"`: A dictionary like {{"type": "bar", "title": "Comparison of X and Y"}}.
            * `"chart_data"`: A dictionary containing the actual data needed for the chart, extracted or summarized from the text/table. It MUST have "labels" (list of strings) and "values" (list of numbers). Example: {{"labels": ["A", "B", "C"], "values": [50, 80, 30]}}.
            Omit BOTH fields if no simple chart is appropriate or if you cannot reliably extract the labels and values.

        Here is the text chunk (potentially including table data):
        ---
        {prompt_content[:15000]}
        ---
        """ # Increased context slightly for tables

        try:
            # ... (Rest of the try/except block remains the same)
            response = model.generate_content(prompt)
            if not response.parts: return {}
            response_text = response.text.strip().lstrip('```json').rstrip('```')
            if not response_text: return {}
            structured_data = json.loads(response_text)
            self.log("Successfully received and parsed structured content for chunk.")
            return structured_data
        except json.JSONDecodeError as e: self.log(f"ERROR: Failed to parse JSON. {e}\nRaw: {response_text[:500]}..."); return {}
        except Exception as e: self.log(f"ERROR: LLM call failed. {e}"); return {}

    # --- UPDATED: Processes tables before chunking and sends table text to LLM ---
    def run(self):
        self.log("Starting content extraction (Text, Tables)...")
        pdf_path = self.sm.get("input_pdf_path")
        tone = self.sm.get("tone") or "Beginner"
        slide_count = self.sm.get("slide_count") or 10
        if not pdf_path: self.log("ERROR: No input_pdf_path found."); return

        # Extract text and table DataFrames
        full_text, extracted_tables = self._extract_text_and_tables_from_pdf(pdf_path)

        # Convert tables to Markdown strings for easier inclusion in prompts
        table_markdowns = [table.to_markdown(index=False) for table in extracted_tables] if extracted_tables else []

        if not full_text and not table_markdowns:
             self.log("No text or tables extracted. Cannot proceed.")
             return

        # Combine text and table markdown for chunking (or decide how to associate tables with text chunks)
        # Simple approach: append all table text at the end of the document text before chunking.
        combined_content = full_text
        if table_markdowns:
            combined_content += "\n\n=== Appendix: Extracted Tables ===\n"
            for i, md in enumerate(table_markdowns):
                combined_content += f"\n--- Table {i+1} ---\n{md}\n"

        # Chunk the combined content
        content_chunks = chunk_text(combined_content, chunk_size=self.chunk_size, overlap=self.overlap)
        self.log(f"Split content into {len(content_chunks)} chunks.")

        all_chapters = []
        for i, chunk in enumerate(content_chunks):
            self.log(f"Processing chunk {i+1}/{len(content_chunks)}...")
            # For this simple approach, we pass an empty list for tables_in_chunk
            # as table data is now part of the main chunk text.
            # A more advanced approach would track which tables belong to which text chunk.
            structured_content = self._get_structured_content_from_llm(chunk, [], tone, slide_count)
            if structured_content and "chapters" in structured_content:
                all_chapters.extend(structured_content["chapters"])
            else: self.log(f"No valid 'chapters' structure returned for chunk {i+1}.")

        if all_chapters:
            self.update_state("chapters", all_chapters)
            self.log(f"Content processed. Found {len(all_chapters)} chapters total.")
            # self.sm.save("shared_state_after_content.json")
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
