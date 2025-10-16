# Multi-Agent PPT Generator 

This project is an autonomous multi-agent AI system that generates complete educational presentations from a syllabus PDF. It demonstrates a modular, collaborative AI architecture built from scratch, capable of understanding content, designing slides, and sourcing relevant visuals automatically.

---

## Features

* **PDF to Presentation:** Automatically converts text from a syllabus PDF into a structured `.pptx` deck.
* **AI-Powered Content:** Uses Google's Gemini API to analyze, summarize, and structure the content into topics, key points, and quiz questions.
* **Multi-Agent System:** Built with independent agents (Content, Format, Design, Media) that collaborate via a shared JSON state.
* **Automated Visuals:** Fetches relevant, high-quality images from the Pexels API to illustrate slides.
* **Custom Theming:** Applies a consistent and professional design using a master PowerPoint template.

---

## Architecture

The system operates as a pipeline of specialized agents. Each agent performs a specific task and passes its output to the next agent through a shared state manager.

1.  **`ContentAgent`**: Reads the input PDF and uses the Gemini API to extract topics, summaries, and image hints.
2.  **`FormatAgent`**: Takes the structured content and creates a slide-by-slide blueprint (e.g., title slide, content slide, quiz slide).
3.  **`DesignAgent`**: Selects the master PowerPoint template to define the overall theme.
4.  **`ExternalMediaAgent`**: Reads the image hints, searches the Pexels API, and downloads relevant images.
5.  **`PresentationAgent`**: Assembles the final `.pptx` file using the blueprint, theme, and downloaded images.

---

## Tech Stack

* **Core Language:** Python 3.11
* **AI Model:** Google Gemini 2.5 Pro
* **Key Libraries:**
    * `google-generativeai`: For interacting with the Gemini LLM.
    * `PyMuPDF`: For high-performance text extraction from PDF files.
    * `python-pptx`: To create and manipulate PowerPoint (`.pptx`) files.
    * `requests`: To communicate with the Pexels web API.
    * `python-dotenv`: To manage secret API keys.
* **External APIs:**
    * Google Gemini API
    * Pexels API

---

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

* Python 3.9+
* A PDF viewer to see the output

### Installation & Setup

1.  **Clone the repository (remember to change `YourUsername`):**
    ```bash
    git clone [https://github.com/YourUsername/multi-agent-ppt-generator.git](https://github.com/YourUsername/multi-agent-ppt-generator.git)
    cd multi-agent-ppt-generator
    ```

2.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your API keys:**
    * Create a file named `.env` in the project's root directory.
    * Add your API keys in the following format:
        ```env
        GEMINI_API_KEY="Your-Google-AI-Studio-Key"
        PEXELS_API_KEY="Your-Pexels-API-Key"
        ```

4.  **Add Input Files:**
    * Place the syllabus you want to process inside the `data/` folder and name it `syllabus.pdf`.
    * Ensure you have a PowerPoint template file named `edutor_theme.pptx` inside the `templates/` folder.

### Usage

To run the entire pipeline, execute the main script from the root directory:
```bash
python main.py