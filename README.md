# Multi-Agent PPT Generator

This project is an autonomous multi-agent AI system that generates complete educational presentations from a syllabus PDF. It demonstrates a modular, collaborative AI architecture built from scratch using Python. The system can understand content, structure it logically, design slides using templates, source relevant visuals (stock photos or AI-generated diagrams), and output a finished `.pptx` presentation. An optional PDF conversion step is also included.

---

## Features

* **PDF to Presentation:** Automatically converts text from a syllabus PDF into a structured `.pptx` deck.
* **AI-Powered Content:** Uses Google's Gemini API to analyze, summarize, structure content, generate quiz questions, and suggest visuals.
* **Customizable Output:** Allows users to select the target audience tone (Beginner, Intermediate, Expert) and approximate slide count via the UI.
* **Multi-Agent System:** Built with independent agents (Content, Format, Design, Media, Presentation) collaborating via a shared JSON state.
* **Dynamic Visuals:**
    * Generates custom diagrams using **Graphviz** for processes or flows identified by the AI.
    * Fetches relevant stock photos from the **Pexels API** as a fallback.
* **Multiple Themes:** Supports different visual styles through user-selectable PowerPoint templates.
* **Web Interface:** Includes a simple web UI built with **Streamlit** for easy file uploads and option selection.
* **PDF Conversion (Optional):** Can automatically convert the final `.pptx` to `.pdf` using LibreOffice.

---

## Architecture

The system operates as a pipeline of specialized agents orchestrated by `main.py`. Each agent performs a specific task and communicates through a `StateManager`.

1.  **`ContentAgent`**: Reads the input PDF (`PyMuPDF`), calls the Gemini API with user customizations (tone, length), extracts topics/summaries/quiz questions, and generates image hints or Graphviz DOT code.
2.  **`FormatAgent`**: Translates the structured content into a slide-by-slide blueprint.
3.  **`DesignAgent`**: Reads the user's theme choice and sets the path to the correct `.pptx` template.
4.  **`ExternalMediaAgent`**: Prioritizes generating diagrams from DOT code using `graphviz`. If no code is present, it searches Pexels via API using the image hint and downloads an image.
5.  **`PresentationAgent`**: Assembles the final `.pptx` file using `python-pptx`, applying the chosen template, populating text, inserting visuals into appropriate layouts, and handling quiz data correctly.
6.  **(Optional) PDF Conversion**: `main.py` uses `subprocess` to call LibreOffice (if installed and in PATH) to convert the `.pptx` to `.pdf`.

---

## Tech Stack

* **Core Language:** Python 3.11
* **AI Model:** Google Gemini 2.5 Pro (via Google AI API)
* **Web Framework:** Streamlit
* **Diagram Generation:** Graphviz
* **Key Python Libraries:**
    * `google-generativeai`: Gemini API interaction.
    * `PyMuPDF`: PDF text extraction.
    * `python-pptx`: PowerPoint file creation.
    * `requests`: Pexels API interaction.
    * `python-dotenv`: Environment variable management.
    * `streamlit`: Web UI creation.
    * `graphviz`: Diagram rendering.
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
* Graphviz software installed **and** added to your system's PATH. ([Download](https://graphviz.org/download/))
* (Optional) LibreOffice installed **and** added to your system's PATH for PDF conversion. ([Download](https://www.libreoffice.org/download/download-libreoffice/))
* A PowerPoint viewer (like PowerPoint, LibreOffice Impress, Google Slides)

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
    * Create a file named `.env` in the project's root directory.
    * Add your API keys:
        ```env
        GEMINI_API_KEY="Your-Google-AI-Studio-Key"
        PEXELS_API_KEY="Your-Pexels-API-Key"
        ```

4.  **Prepare Input Files:**
    * Ensure you have at least one `.pptx` template file (e.g., `edutor_theme.pptx`) inside the `templates/` folder. Add more templates (`dark_mode.pptx`, `minimalist.pptx`) if you want theme options.

### Usage (Web UI)

The easiest way to use the generator is via the Streamlit web interface:

1.  Make sure you are in the project's root directory in your terminal.
2.  Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```
3.  Your browser should open the app automatically.
4.  Use the sidebar to select options (Theme, Tone, Slide Count).
5.  Upload your syllabus PDF.
6.  Click "Generate Presentation".
7.  Download buttons for the `.pptx` (and `.pdf` if conversion succeeds) will appear.

### Usage (Command Line - Basic)

You can also run the pipeline directly from the command line for testing:

1.  Place your syllabus inside the `data/` folder and name it `syllabus.pdf`.
2.  Run the main script:
    ```bash
    python main.py
    ```
    This will use default settings (e.g., "Beginner" tone, 10 slides, "edutor\_theme.pptx"). The output files will be saved in the `output/` folder.

---

##  Example Output

Here is an example of a slide generated by the system, featuring AI-structured text and a relevant image:

![Example Slide](docs/example_slide.png)

*(Optional: Add an example of a generated diagram if you have one)*