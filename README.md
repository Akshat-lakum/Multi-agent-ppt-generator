# Multi-Agent PPT Generator 🤖

This project is an autonomous multi-agent AI system that generates complete educational presentations from a syllabus PDF. It demonstrates a modular, collaborative AI architecture built from scratch using Python. The system can understand content (using layout-aware parsing and chunking for large files), structure it logically, generate speaker notes, design slides using templates, source relevant visuals (AI-suggested placeholder charts, AI-generated diagrams, or stock photos), perform AI-driven quality checks, and output a finished `.pptx` presentation. An optional PDF conversion step is also included.

---

## ✨ Features

* **PDF to Presentation:** Automatically converts text from a syllabus PDF (using layout-aware parsing and chunking for large files) into a structured `.pptx` deck.
* **AI-Powered Content:** Uses Google's Gemini API to analyze, summarize, structure content, generate **speaker notes**, generate quiz questions, and suggest visuals.
* **Customizable Output:** Allows users to select the target audience tone (Beginner, Intermediate, Expert) and approximate slide count via the UI.
* **Multi-Agent System:** Built with independent agents (Content, Format, Design, Media, Presentation, QA) collaborating via a shared JSON state.
* **Dynamic Visuals (Prioritized):**
    * Generates **placeholder charts** (bar, line) using Matplotlib/Seaborn based on AI suggestions.
    * Generates custom diagrams using **Graphviz** for processes or flows identified by the AI.
    * Fetches relevant stock photos from the **Pexels API** as a fallback.
* **Multiple Themes:** Supports different visual styles through user-selectable PowerPoint templates.
* **AI Speaker Notes:** Generates detailed speaker notes for each content slide.
* **AI Quality Assurance:** Includes a QA agent that uses Gemini to review the generated slide plan for clarity, accuracy, and relevance.
* **Web Interface:** Includes a simple web UI built with **Streamlit** for easy file uploads and option selection.
* **PDF Conversion (Optional):** Can automatically convert the final `.pptx` to `.pdf` using LibreOffice.

---

## 🏛️ Architecture

The system operates as a pipeline of specialized agents orchestrated by `main.py`. Each agent performs a specific task and communicates through a `StateManager`.

1.  **`ContentAgent`**: Reads the PDF using layout-aware extraction (`PyMuPDF`), chunks large texts, calls Gemini API with user customizations, extracts topics/summaries/quizzes/**notes**, and generates hints for charts, diagrams (DOT code), or images.
2.  **`FormatAgent`**: Translates the structured content into a slide-by-slide blueprint.
3.  **`DesignAgent`**: Reads the user's theme choice and sets the path to the correct `.pptx` template.
4.  **`ExternalMediaAgent`**: Prioritizes generating placeholder charts (`matplotlib`/`seaborn`) from AI suggestions. If no suggestion, it generates diagrams from DOT code (`graphviz`). If neither, it searches Pexels via API using the image hint.
5.  **`PresentationAgent`**: Assembles the final `.pptx` file (`python-pptx`), applying the theme, populating text/**notes**, and inserting visuals.
6.  **`QAAgent`**: Sends the generated slide plan back to Gemini for a quality review based on clarity, accuracy, and relevance.
7.  **(Optional) PDF Conversion**: `main.py` uses `subprocess` to call LibreOffice for `.pptx` to `.pdf` conversion.

---

## 🛠️ Tech Stack

* **Core Language:** Python 3.11
* **AI Model:** Google Gemini 2.5 Pro (via Google AI API)
* **Web Framework:** Streamlit
* **Diagram Generation:** Graphviz
* **Chart Generation:** Matplotlib, Seaborn, Pandas, Numpy
* **Key Python Libraries:**
    * `google-generativeai`: Gemini API interaction.
    * `PyMuPDF`: PDF text extraction.
    * `python-pptx`: PowerPoint file creation.
    * `requests`: Pexels API interaction.
    * `python-dotenv`: Environment variable management.
    * `streamlit`: Web UI creation.
    * `graphviz`: Diagram rendering library.
    * `matplotlib`, `seaborn`, `pandas`, `numpy`: Chart generation and data handling.
* **External APIs:**
    * Google AI (Gemini)
    * Pexels API
* **External Software (Optional):**
    * LibreOffice (for PDF conversion)

---

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

* Python 3.9+
* Git
* Graphviz software installed **and** added to system PATH. ([Download](https://graphviz.org/download/))
* (Optional) LibreOffice installed **and** added to system PATH. ([Download](https://www.libreoffice.org/download/download-libreoffice/))
* A PowerPoint viewer

### Installation & Setup

1.  **Clone the repository (replace `Akshat-lakum`):**
    ```bash
    git clone [https://github.com/Akshat-lakum/multi-agent-ppt-generator.git](https://github.com/Akshat-lakum/multi-agent-ppt-generator.git)
    cd multi-agent-ppt-generator
    ```

2.  **Install required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up API keys:**
    * Create `.env` file in the root directory.
    * Add keys:
        ```env
        GEMINI_API_KEY="Your-Google-AI-Studio-Key"
        PEXELS_API_KEY="Your-Pexels-API-Key"
        ```

4.  **Prepare Input Files:**
    * Ensure template files (e.g., `edutor_theme.pptx`) are in `templates/`.

### Usage (Web UI)

1.  Navigate to the project's root directory in your terminal.
2.  Run:
    ```bash
    streamlit run app.py
    ```
3.  Use the sidebar for options, upload PDF, click "Generate".
4.  Download buttons appear upon completion.

### Usage (Command Line - Basic)

1.  Place `syllabus.pdf` in `data/`.
2.  Run:
    ```bash
    python main.py
    ```
    Output files are saved in `output/`.

---

## ✨ Example Output

Here is an example of a slide generated by the system:

![Example Slide](docs/example_slide.png)

*(Optional: Add an example of a generated diagram or chart)*