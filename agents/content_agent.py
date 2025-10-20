# agents/content_agent.py
# ContentAgent updated with Camelot for basic table extraction.

from .base_agent import BaseAgent
import fitz # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import pytesseract
from PIL import Image
import io
import camelot # <-- New import for table extraction
import pandas as pd # <-- Import pandas for table data structure

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
    Uses layout-aware text extraction (with OCR fallback), attempts table extraction
    with Camelot, and uses Gemini API to structure content.
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

    # --- UPDATED: Includes Table Extraction Attempt ---
    def _extract_text_and_tables_from_pdf(self, pdf_path: str) -> tuple[str, list[pd.DataFrame]]:
        """
        Extracts text (layout-aware with OCR fallback) AND tables from a PDF.
        Returns a tuple: (full_text_string, list_of_table_dataframes).
        """
        if not os.path.exists(pdf_path):
            self.log(f"ERROR: PDF file not found at {pdf_path}")
            return "", []

        full_text = ""
        extracted_tables = []
        doc = None

        # --- Part 1: Text Extraction (using PyMuPDF + OCR Fallback) ---
        try:
            # (Your existing PyMuPDF + OCR logic goes here - slightly modified)
            doc = fitz.open(pdf_path)
            pymu_text_check = ""
            for page_num, page in enumerate(doc):
                blocks = page.get_text("blocks")
                blocks.sort(key=lambda b: (b[1], b[0]))
                page_text = "".join([b[4] for b in blocks])
                if len(page_text.strip()) > 50:
                    pymu_text_check += f"\n--- Page {page_num + 1} ---\n" + page_text

            if len(pymu_text_check.strip()) > 100:
                self.log(f"Extracted {len(pymu_text_check)} characters (layout-aware PyMuPDF)")
                full_text = pymu_text_check
            else:
                self.log("PyMuPDF found minimal text. Attempting OCR...")
                ocr_full_text = ""
                for page_num, page in enumerate(doc):
                    # (OCR logic using pytesseract as before)
                    # ... Ensure it adds text to ocr_full_text ...
                    pix = page.get_pixmap(); img = Image.open(io.BytesIO(pix.pil_tobytes("png")))
                    try:
                        page_ocr_text = pytesseract.image_to_string(img, lang='eng')
                        ocr_full_text += f"\n--- OCR Page {page_num + 1} ---\n" + page_ocr_text
                    except pytesseract.TesseractNotFoundError: self.log("ERROR: Tesseract OCR not found."); return "", []
                    except Exception as ocr_e: self.log(f"ERROR: OCR failed for page {page_num+1}. {ocr_e}")

                if len(ocr_full_text.strip()) > 100:
                    self.log(f"Extracted {len(ocr_full_text)} characters (OCR)")
                    full_text = ocr_full_text
                else:
                    self.log("OCR also found minimal text.")
                    full_text = "" # Proceed without text if both fail

        except Exception as e:
            self.log(f"ERROR during text extraction: {e}")
            full_text = "" # Ensure full_text is defined even on error
        finally:
             if doc: doc.close()

        # --- Part 2: Table Extraction (using Camelot) ---
        self.log("Attempting table extraction with Camelot...")
        try:
            # Use Camelot to read tables from all pages
            # 'stream' method is good for tables with clear lines, 'lattice' for tables without lines
            tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice', suppress_stdout=True) # Try 'stream' if 'lattice' fails
            
            if tables:
                self.log(f"Camelot found {tables.n} potential tables.")
                for i, table in enumerate(tables):
                    self.log(f"--- Table {i+1} (Page {table.page}) ---")
                    # table.df is the pandas DataFrame
                    print(table.df.head().to_string()) # Print first few rows of the table to console
                    extracted_tables.append(table.df)
            else:
                self.log("Camelot found no tables.")
                
        except ImportError:
             self.log("WARNING: Camelot library not found or dependencies missing. Skipping table extraction.")
        except Exception as e:
            self.log(f"ERROR during table extraction with Camelot: {e}")

        return full_text, extracted_tables
    # ------------------------------------

    def _get_structured_content_from_llm(self, text_chunk: str, tone: str, slide_count: int) -> dict:
        # ... (This function remains unchanged from the mind map version)
        # ... (Includes requests for speaker notes, diagrams, mind maps, charts) ...
        if not text_chunk: return {}
        self.log(f"Sending chunk (length: {len(text_chunk)}) to Gemini API...")
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        prompt = f"""
        You are an expert educational content designer... (prompt unchanged) ...

        Here is the text chunk:
        ---
        {text_chunk}
        ---
        """
        try:
            response = model.generate_content(prompt)
            # ... (Rest of try/except block remains the same)
            if not response.parts: return {}
            response_text = response.text.strip().lstrip('```json').rstrip('```')
            if not response_text: return {}
            structured_data = json.loads(response_text)
            self.log("Successfully received and parsed structured content for chunk.")
            return structured_data
        except json.JSONDecodeError as e: self.log(f"ERROR: Failed to parse JSON. {e}\nRaw: {response_text[:500]}..."); return {}
        except Exception as e: self.log(f"ERROR: LLM call failed. {e}"); return {}

    def run(self):
        self.log("Starting content extraction (Text, Tables)...")
        pdf_path = self.sm.get("input_pdf_path")
        tone = self.sm.get("tone") or "Beginner"
        slide_count = self.sm.get("slide_count") or 10
        if not pdf_path: self.log("ERROR: No input_pdf_path found."); return

        # --- Call the updated extraction function ---
        full_text, extracted_tables = self._extract_text_and_tables_from_pdf(pdf_path)
        # ------------------------------------------

        # Save extracted tables to state (optional, for potential future use by ChartAgent)
        # Note: DataFrames aren't directly JSON serializable, convert or handle later
        # For now, just logging them is enough to confirm extraction.
        if extracted_tables:
             self.log(f"Successfully extracted {len(extracted_tables)} tables.")
             # You could add logic here to convert tables to a string/JSON format
             # and potentially add them to the state manager if needed.
             # self.sm.update("extracted_tables", [t.to_dict('records') for t in extracted_tables])


        if not full_text:
             self.log("No text extracted from PDF. Cannot proceed with LLM analysis.")
             return # Stop if no text was found

        # --- Chunking and LLM processing remain the same ---
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
