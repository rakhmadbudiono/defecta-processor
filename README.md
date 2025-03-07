# Defecta Processor

## Overview

Defecta Processor is a Streamlit application designed to extract product information from distributor files in Excel and PDF formats. The application utilizes OpenAI's language model to process unstructured text and extract relevant product details, including prices and discounts.

## Features

- Upload distributor files in Excel or PDF format.
- Extract product information, including names, final prices, and distributors.
- Search for specific products within the uploaded distributor files.
- Display results in a user-friendly table format.

## Requirements

- Python 3.9 or higher
- Streamlit
- Pandas
- OpenAI
- pdfplumber
- fuzzywuzzy
- Pydantic

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/defecta-processor.git
   cd defecta-processor
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Alternatively, you can create a virtual environment and install the required packages:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install streamlit pandas openai pdfplumber fuzzywuzzy pydantic
   ```

## Usage

1. Run the Streamlit application:

   ```bash
   streamlit run src/app.py
   ```

2. Open your web browser and navigate to `http://localhost:8501`.

3. Upload your distributor files (Excel or PDF) using the file uploader.

4. Use the search bar to find specific products within the uploaded files.

5. View the extracted product information displayed in a table format.
