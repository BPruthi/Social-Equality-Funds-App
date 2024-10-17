import os
import shutil
import streamlit as st
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from url_fetcher import find_top_search_results  
from vector_embed import load_from_directory, create_embeddings, create_chatbot  # Import chatbot functions
import tempfile
from PIL import Image

# Make sure these imports are at the top of your file
import traceback
import pandas as pd
from io import BytesIO

# Loading Tab Icon
im = Image.open("./src/logo.ico")

# Setting App Title
st.set_page_config(
    page_title="Social Equality Funds", page_icon=im
)

# Removing Made With Streamlit from Footer.
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Initialize session state for all relevant variables
if 'company_name' not in st.session_state:
    st.session_state['company_name'] = ''
if 'keyword' not in st.session_state:
    st.session_state['keyword'] = ''
if 'urls' not in st.session_state:
    st.session_state['urls'] = []
if 'selected_urls' not in st.session_state:
    st.session_state['selected_urls'] = []
if 'processed_data' not in st.session_state:
    st.session_state['processed_data'] = {}
if 'document_embeddings' not in st.session_state:
    st.session_state['document_embeddings'] = None
if 'vectorstore' not in st.session_state:
    st.session_state['vectorstore'] = None
if 'pdf_files' not in st.session_state:
    st.session_state['pdf_files'] = []  # Hold the list of PDFs for confirmation
if 'final_pdf_selection' not in st.session_state:
    st.session_state['final_pdf_selection'] = []  # Hold user-selected PDFs for final processing

# Function to download PDFs from a given URL
def download_pdf(url, folder_path):
    response = requests.get(url)
    file_name = os.path.basename(urlparse(url).path)
    file_path = os.path.join(folder_path, file_name)
    
    # Write the PDF to the local directory
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path

# Function to scrape PDFs from HTML pages
def scrape_pdfs_from_html(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        pdf_links = []

        # Find all <a> tags with href attributes ending in .pdf
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                pdf_links.append(urljoin(url, href))
        
        return pdf_links

    except Exception as e:
        st.error(f"Error scraping PDFs from {url}: {str(e)}")
        return []

# Function to process URLs to scrape PDFs but not save them yet
def process_urls(urls):
    pdf_files = []  # Temporary list of all found PDFs

    for url in urls:
        try:
            # Check if the URL ends with '.pdf'
            if url.lower().endswith('.pdf'):
                pdf_files.append(url)
            else:
                # Scrape PDFs from HTML pages
                pdf_files_from_html = scrape_pdfs_from_html(url)
                pdf_files.extend(pdf_files_from_html)
        except Exception as e:
            st.error(f"Error processing URL {url}: {str(e)}")

    return pdf_files  # Return the list of PDFs for user confirmation

# Function to save user-selected PDFs to the 'pdf_docs' folder
def save_selected_pdfs(selected_pdfs):
    folder_path = "pdf_docs"
    
    # Delete the folder if it exists and recreate it
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)

    for pdf_url in selected_pdfs:
        download_pdf(pdf_url, folder_path)

    return folder_path  # Return folder path for further processing


col1, mid, col2 = st.columns([1, 2, 18])

with col1:
    st.image("./src/logo.ico", width=77)
with col2:
    st.title('Social Equality Funds')

# User input for company name and keyword
st.session_state['company_name'] = st.text_input("Company Name", st.session_state['company_name'])
st.session_state['keyword'] = st.text_input("Keyword", st.session_state['keyword'])

# Fetch URLs on submit
if st.button("Submit"):
    st.session_state['urls'] = find_top_search_results(st.session_state['company_name'], st.session_state['keyword'])
    st.session_state['selected_urls'] = []  # Reset selected URLs when fetching new ones
    st.session_state['processed_data'] = {}  # Reset processed data when fetching new URLs

# Display fetched URLs and allow selection if URLs are available
if st.session_state['urls']:
    st.subheader("Select URLs")
    
    selected_urls = []
    
    # Display checkboxes for each URL and allow user to select them
    for url in st.session_state['urls']:
        if st.checkbox(url, key=url):
            selected_urls.append(url)
    
    # Option to add custom URLs
    custom_urls = st.text_input("Add Custom URLs (comma-separated)")
    if custom_urls:
        custom_url_list = [url.strip() for url in custom_urls.split(',') if url.strip()]
        selected_urls.extend(custom_url_list)

    # Update the selected URLs in session state
    st.session_state['selected_urls'] = selected_urls

    # Submit button to process selected URLs and get list of PDFs
    if st.button("Submit Selected URLs"):
        if st.session_state['selected_urls']:
            with st.spinner("Processing URLs..."):
                # Process the URLs to find PDFs, but don't save them yet
                st.session_state['pdf_files'] = process_urls(st.session_state['selected_urls'])
            
            if st.session_state['pdf_files']:
                st.success("PDFs found! Please select the PDFs to save.")
            else:
                st.warning("No PDFs found.")
        else:
            st.warning("Please select at least one URL.")



# Display found PDFs and allow user to select them for final saving
if st.session_state['pdf_files']:
    st.subheader("Select PDFs to save")
    
    selected_pdfs = []
    
    for idx, pdf_url in enumerate(st.session_state['pdf_files']):
        file_name = pdf_url.split('/')[-1]
        if st.checkbox(file_name, key=f"pdf_{idx}"):
            selected_pdfs.append(pdf_url)
    
    st.session_state['final_pdf_selection'] = selected_pdfs

    # Submit button to save the selected PDFs
    if st.button("Save Selected PDFs"):
        if st.session_state['final_pdf_selection']:
            try:
                with st.spinner("Saving selected PDFs..."):
                    folder_path = save_selected_pdfs(st.session_state['final_pdf_selection'])
                    # st.write(f"PDFs saved to {folder_path}")
                
                # Create embeddings and vector store
                with st.spinner("Processing documents..."):
                    try:
                        st.write("Loading documents from directory...")
                        processed_documents = load_from_directory(folder_path)
                        # st.write(f"Loaded {len(processed_documents)} documents")

                        if not processed_documents:
                            st.error("No documents were loaded for processing.")
                            st.stop()
                        
                        st.write("Creating embeddings...")
                        document_embeddings, vectorstore = create_embeddings(processed_documents)
                        
                        if document_embeddings is None or vectorstore is None:
                            st.error("Failed to create embeddings or vectorstore.")
                            st.stop()
                        
                        st.session_state['document_embeddings'] = document_embeddings
                        st.session_state['vectorstore'] = vectorstore
                        st.success("Documents processed successfully!")
                        
                    except Exception as e:
                        st.error(f"Error during document processing: {str(e)}")
                        st.error(f"Traceback: {traceback.format_exc()}")
            except Exception as e:
                st.error(f"Error saving PDFs: {str(e)}")
                st.error(f"Traceback: {traceback.format_exc()}")
        else:
            st.warning("Please select at least one PDF to save.")

# Allow chatbot functionality if vectorstore is available
if st.session_state['vectorstore'] is not None:
    try:
        st.subheader("Chatbot")

        # Ask user for a question and submit via a button
        user_question = st.text_input("Ask a question:")

        if st.button("Submit Question"):
            if user_question:
                try:
                    with st.spinner("Processing your query..."):
                        chatbot_response = create_chatbot(
                            st.session_state['document_embeddings'], 
                            st.session_state['vectorstore'], 
                            user_question
                        )
                        st.write(chatbot_response)
                except Exception as e:
                    st.error(f"Error processing question: {str(e)}")
                    st.error(f"Traceback: {traceback.format_exc()}")
            else:
                st.warning("Please enter a question before submitting.")

        # Excel file processing
        uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

        if uploaded_file is not None:
            try:
                current_file_contents = uploaded_file.getvalue()
                
                # Check if this is a new file
                if 'last_processed_file' not in st.session_state or \
                st.session_state['last_processed_file'] != current_file_contents:
                    
                    st.session_state['last_processed_file'] = current_file_contents
                    
                    with st.spinner("Processing Excel file..."):
                        try:
                            df = pd.read_excel(BytesIO(current_file_contents))
                            # st.write(f"Excel file loaded. Columns found: {', '.join(df.columns.tolist())}")

                            if 'QUESTIONS' not in df.columns:
                                st.error("The Excel file must contain a 'QUESTIONS' column.")
                            else:
                                responses = []
                                total_questions = len(df['QUESTIONS'])
                                st.write(f"Found {total_questions} questions to process")

                                progress_bar = st.progress(0)
                                
                                for index, question in enumerate(df['QUESTIONS']):
                                    try:
                                        # st.write(f"Processing question {index + 1}: {question}")
                                        chatbot_response = create_chatbot(
                                            st.session_state['document_embeddings'],
                                            st.session_state['vectorstore'],
                                            question
                                        )
                                        responses.append(chatbot_response)
                                        progress_bar.progress((index + 1) / total_questions)
                                    except Exception as e:
                                        st.error(f"Error processing question {index + 1}: {str(e)}")
                                        responses.append(f"Error: {str(e)}")

                                result_df = pd.DataFrame({
                                    'QUESTIONS': df['QUESTIONS'],
                                    'RESPONSES': responses
                                })

                                output = BytesIO()
                                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                    result_df.to_excel(writer, index=False, sheet_name='Chatbot Responses')
                                    workbook = writer.book
                                    worksheet = writer.sheets['Chatbot Responses']
                                    wrap_format = workbook.add_format({'text_wrap': True})
                                    worksheet.set_column('A:A', 50)
                                    worksheet.set_column('B:B', 100, wrap_format)

                                st.session_state['excel_processed'] = output.getvalue()
                                st.success("Excel file processed successfully!")

                        except Exception as e:
                            st.error(f"Error processing Excel file: {str(e)}")
                            st.error(f"Traceback: {traceback.format_exc()}")

                if 'excel_processed' in st.session_state:
                    try:
                        st.download_button(
                            label="Download Responses",
                            data=st.session_state['excel_processed'],
                            file_name="chatbot_responses.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"Error creating download button: {str(e)}")
            
            except Exception as e:
                st.error(f"Error handling uploaded file: {str(e)}")
                st.error(f"Traceback: {traceback.format_exc()}")
    
    except Exception as e:
        st.error(f"Error in chatbot section: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")