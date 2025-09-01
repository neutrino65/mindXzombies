# MoodSense 🧠💻

## Overview

This project is a Mental Wellness Assistant that uses a combination of Optical Character Recognition (OCR) and Generative AI to monitor for signs of negative or depressive thoughts on your computer screen. It works by periodically taking a screenshot, extracting the text from it, and then analyzing that text for sentiment. If a negative thought pattern is detected, it triggers a supportive, non-intrusive pop-up message to help you reframe your thinking.

The system is broken down into three main Python scripts:

- **image_to_text.py**: Handles the screenshot capture and text extraction.
- **sentiment_analyzer.py**: Uses the Google Gemini API to perform sentiment analysis.
- **main.py**: The core orchestrator that automates the entire process in a continuous loop.

## Key Features

- **Continuous Monitoring**: The `main.py` script runs in a loop, periodically checking your screen for text every 10 seconds.
- **Real-time Screenshot**: Captures a snapshot of your screen with a customizable delay to analyze displayed text. The temporary screenshot is automatically deleted after processing.
- **Intelligent Text Extraction**: Utilizes OpenCV and PyTesseract to preprocess images and accurately extract text. It also offers an interactive mode and can process a single image or an entire folder of images.
- **AI-Powered Sentiment Analysis**: Leverages the Gemini 2.0 Flash API to detect negative, depressive, or violent language. The API call is highly constrained to return only a simple True or False.
- **Supportive Alerts**: When a negative thought is detected, a native Windows pop-up alert appears with a helpful, comforting message. This is designed to be a gentle reminder, not an alarm.
- **Cross-Platform (with caveats)**: While the sentiment analysis works everywhere, the screenshot functionality is optimized for Windows and requires specific dependencies, with clear warnings for environments like WSL.

## Project Structure

```
.
├── extracted/            # Folder for extracted text output
├── images/               # Folder for temporary screenshots and user-provided images
├── main.py               # Main orchestrator script
├── image_to_text.py      # Script for OCR and screenshot functions
└── sentiment_analyzer.py # Script for AI-powered sentiment analysis
```

## Setup and Installation

### Prerequisites

- **Python 3.x**: Ensure you have Python installed on your system.
- **Tesseract OCR**: This is a core dependency for the OCR process. You must install it separately from the Python package.
  - **Windows**: [Download and install from the Tesseract GitHub Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
  - **macOS**: `brew install tesseract`
  - **Linux**: `sudo apt-get install tesseract-ocr`
- **Google Gemini API Key**: This project requires an API key for the Gemini API. While the `sentiment_analyzer.py` file has an empty variable, the project is designed to be used in an environment where the key is provided automatically.

### Python Dependencies

Install the required Python libraries using pip:

```sh
pip install opencv-python pytesseract pillow pyautogui requests
```

> **Note:** The `pyautogui` library is used for taking screenshots. If you are running this in a headless or WSL environment, this library will likely fail to import, and the screenshot functionality will be automatically disabled.

## How to Use

The project is designed to be run from the command line, but also includes an interactive mode.

### Run the Main Orchestrator

To start the continuous monitoring loop, simply run the `main.py` script. It will handle the entire workflow from taking screenshots to showing alerts.

```sh
python main.py
```

### Manual Usage (Advanced)

You can also run the individual scripts for specific tasks.

#### image_to_text.py

This script can be used to either process a screenshot or extract text from existing images.

**Take a screenshot and extract text:**

```sh
python image_to_text.py --screenshot --delay 5
```

This will take a screenshot after a 5-second delay and save the extracted text to a file in the `extracted` folder.

**Process an image file or a folder of images:**

```sh
# Process a single image
python image_to_text.py --input images/my_document.png

# Process all images in a folder
python image_to_text.py --input images/
```

The extracted text will be saved to `extracted/extracted_text.txt`.

#### sentiment_analyzer.py

This script takes a string of text as a command-line argument and performs sentiment analysis.

```sh
python sentiment_analyzer.py "I feel so tired and unmotivated today."
```

The output will be either `negative behavioral True` or `negative behavioral False`.

---

