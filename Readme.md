# Social Equality Funds Chatbot

This Streamlit-based web app fetches, processes, and embeds PDF documents to enable chatbot interactions. The app allows users to scrape PDFs from given URLs, process those PDFs, and create embeddings to be queried using a custom chatbot. Additionally, users can upload Excel files for processing.

# Features

1. URL Scraping: Fetch and scrape PDFs from provided URLs.
2. Custom URL Addition: Add custom URLs for PDF scraping.
3. PDF Processing: Select, save, and embed PDFs for querying.
4. Excel Upload: Upload Excel files and integrate their data into the chatbot.
5. Chatbot: Use a custom chatbot to ask questions based on processed documents.

# Prerequisites

Before running the app, ensure you have the following installed:

> Python 3.11+
> Streamlit
> Requests
> BeautifulSoup
> PIL (Pillow)
> LangChain (for embeddings and vector store creation)
> Chroma (for vector storage)
> OpenAI Embeddings (ensure you have the API key)
> Google Search (API Key required)

# Installation

Clone the repository in your system.

Create conda env/ or virtual ennvironment

conda create --prefix ./env python=3.11.4

Install required packages:

    pip install -r requirements.txt

Place your logo.ico in the src folder.

Setup and Running the App
Start the Streamlit app:

    streamlit run app.py --server.port 8080

# App Sections

1. Company Name & Keyword Input: Users can provide a company name and keyword to fetch URLs related to the topic.
2. Submit & Select URLs: Users can fetch top search results, select relevant URLs, and scrape PDF links from those URLs. Alternatively, users can manually input custom URLs for processing.
3. Process PDFs: After scraping, users can select which PDFs to save and process. The selected PDFs will be downloaded and stored in the pdf_docs folder, and embeddings will be created using those documents.
4. Chatbot: Once the documents are embedded, users can interact with the chatbot to ask questions based on the contents of the processed PDFs.
5. Excel Upload: Users can upload an Excel file for processing, and the contents will be embedded alongside the PDFs for querying (The excel must contain a column named "QUESTIONS").

# Code Explanation & Key Functions:

1. scrape_pdfs_from_html(url): Scrapes all PDF links from a given HTML page.
2. download_pdf(url, folder_path): Downloads a PDF file from a URL and saves it to the specified directory.
3. process_urls(urls): Processes a list of URLs, either scraping them for PDFs or directly using them if they are PDFs.
4. save_selected_pdfs(selected_pdfs): Saves selected PDFs to the pdf_docs folder and processes them for embeddings.
5. create_chatbot(): Initializes the chatbot and returns the response based on the user’s question.

# Embedding & Vector Store:

The app uses LangChain and OpenAI embeddings to convert the processed documents into vectors, which are then stored in a vector database (Chroma). This allows for efficient querying by the chatbot.

# Customization

Logo: The app displays a logo (logo.ico) in the sidebar. It can be customized by replacing the file in the src folder.

# License

This is a proprietary licensed application developed for Whistle Stop Capital.

