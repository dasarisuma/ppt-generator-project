# SlideDeck Project

# SlideDeck: Smart Lecture Slide Generator

## Overview

SlideDeck is an intelligent platform designed to assist university lecturers in seamlessly generating formal, high-quality lecture presentations. By leveraging advanced AI models, the tool simplifies the slide creation process—starting from just a topic or a set of input documents—while maintaining academic rigor and visual clarity.

## Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **Image Generation:** Pollinations AI
* **Text & Content Generation:** Graq LLMs

## Features

* Generate slides from a topic or uploaded documents (PDF, DOCX, TXT).
* Specify delivery medium and complexity level.
* AI-powered slide structure generation.
* Editable slide structure interface.
* Detailed content generation for each slide.
* Automatic inclusion of visual aids (diagrams/images) where needed.
* Professional academic styling and formatting.
* Persona-based prompting for tailored content.
* Download generated slides as a PowerPoint (.pptx) file.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd slidedeck
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure environment variables:**
    * Create a file named `.env` in the `slidedeck/` directory.
    * Add your Graq API key:
        ```
        GRAQ_API_KEY="your_graq_api_key_here"
        ```
    * Optionally, set `GRAQ_API_URL` and `POLLINATIONS_API_URL` if they differ from the defaults in the code.
5.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

## Usage

1.  Open the app in your browser.
2.  Choose whether to enter a topic or upload documents.
3.  Provide the necessary details (topic, medium, complexity).
4.  Click "Generate Slide Structure".
5.  Review and edit the generated slide structure (titles, types, order).
6.  Click "Generate Content".
7.  Review the generated content for each slide.
8.  Click "Generate PowerPoint".
9.  Download the resulting `.pptx` file.