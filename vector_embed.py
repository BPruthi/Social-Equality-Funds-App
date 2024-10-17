import os

from langchain_community.document_loaders import CSVLoader,BSHTMLLoader, WebBaseLoader,PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from tqdm import tqdm

import shutil
import tempfile

persist_directory = tempfile.mkdtemp()

# __import__('pysqlite3')
# import sys

# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from dotenv import load_dotenv

# Load environment 
load_dotenv()

open_api_key = os.getenv("OPEN_API_KEY")
embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL"),
                               api_key=open_api_key)


llm = ChatOpenAI(model=os.getenv("LLM"), temperature=0.1, api_key=open_api_key)


def create_embeddings(documents):
    print("In create embeddings")

    # Use 'persist_directory' to create a persistent vector store
    persist_directory = "vector_store_db" 

    # If vectorstore exists, disconnect before deleting
    if os.path.exists(persist_directory):
        try:
            # Attempt to clear Chroma if it's still connected
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
            vectorstore.delete_collection()  # Clear the collection if necessary
            # vectorstore._client.close()  # Ensure the client is closed
        except Exception as e:
            print(f"Error during closing: {e}")

        shutil.rmtree(persist_directory, ignore_errors=True)
        print(f"Removed previous vector store: {persist_directory}")
    
    os.makedirs(persist_directory, exist_ok=True)

    try:
        vectorstore = Chroma.from_documents(documents, embeddings, persist_directory=persist_directory)
    except Exception as e:
        print(f"Error creating vector store: {e}")

    return documents, vectorstore



# def create_embeddings(documents):
#     print("In create embeddings")

#     # Use 'persist_directory' to create a persistent vector store
#     persist_directory = "vector_store_db"  # Path where Chroma will store the vector database

#     # Clear the previous vector store by deleting the directory if necessary
#     if os.path.exists(persist_directory):
#         shutil.rmtree(persist_directory)
#         print("Removed previous vector store")

    
#     os.makedirs(persist_directory, exist_ok=True)
    
#     vectorstore = Chroma.from_documents(documents, embeddings,persist_directory=persist_directory)

#     return documents, vectorstore


def load_from_directory(directory):
    print("Entered in function")
    combined_data = []

    loaders = {
        "pdf": PyPDFLoader,
        "csv": CSVLoader,
        "html": BSHTMLLoader,
        "xlsx": CSVLoader
    }
    try:

        for filename in tqdm(os.listdir(directory)):
            ext = filename.split(".")[-1].lower()  # Ensure extension check is case-insensitive
            if ext in loaders:
                loader_class = loaders[ext]
                loader = loader_class(os.path.join(directory, filename))
                documents = loader.load()
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=250)
                texts = text_splitter.split_documents(documents)
                combined_data.extend(texts)
                
            else:
                loader = WebBaseLoader(os.path.join(directory, filename))
                documents = loader.load()
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=250)
                texts = text_splitter.split_documents(documents)
                combined_data.extend(texts)
        print("SIZE of Combined Data : ",len(combined_data))
        return combined_data
    except Exception as e:
        print(f"Error in Loading Documents {e}")
        return None


def create_chatbot(documents,vectorstore,question_asked):
    
    vectorstore_retreiver = vectorstore.as_retriever(search_kwargs={"k": 5},)

    keyword_retriever = BM25Retriever.from_documents(documents)
    keyword_retriever.k =  5 

    ensemble_retriever = EnsembleRetriever(retrievers=[vectorstore_retreiver,
                                                    keyword_retriever],
                                        weights=[0.5, 0.5])


    template = """
    <|system|>>
    You are a helpful Research Assistant with expertise in human rights and tech accountability.
    You are conducting a research on tech accountability of renowned publicity listed companies accross criterias.

    You follow instructions extremely well.
    Use the following context to answer user question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer
    Think step by step before answering the question.
    CONTEXT: {context}
    </s>
    <|user|>
    {query}
    Please provide the answer and include the sources.
    </s>
    """

    prompt = ChatPromptTemplate.from_template(template)
    output_parser = StrOutputParser()

    chain = (
        {"context": ensemble_retriever, "query": RunnablePassthrough()}
        | prompt
        | llm
        | output_parser
    )

    result = chain.invoke(question_asked)

    return result



# def create_chatbot(documents, vectorstore, user_question):
#     vectorstore_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
#     keyword_retriever = BM25Retriever.from_documents(documents)
#     keyword_retriever.k = 5

#     ensemble_retriever = EnsembleRetriever(retrievers=[vectorstore_retriever, keyword_retriever], weights=[0.5, 0.5])
#     llm = ChatOpenAI(model="gpt-4", temperature=0.1, api_key=open_api_key)

#     template = """
#     <|system|>>
#     You are a helpful Research Assistant with expertise in human rights and tech accountability.
#     You are conducting research on tech accountability of renowned publicly listed companies across criteria.

#     You follow instructions extremely well.
#     Use the following context to answer user question.
#     If you don't know the answer, just say that you don't know, don't try to make up an answer.
#     Think step by step before answering the question.
#     CONTEXT: {context}
#     </s>
#     <|user|>
#     {query}
#     Please provide the answer and include the sources.
#     </s>
#     """

#     prompt = ChatPromptTemplate.from_template(template)
#     output_parser = StrOutputParser()

#     # Retrieve relevant documents based on the user question
#     retrieved_docs = ensemble_retriever.invoke({"query": str(user_question)})

#     # Make sure to extract the text correctly
#     context_text = " ".join(doc['text'] for doc in retrieved_docs if isinstance(doc, dict) and 'text' in doc)

#     # Check if context_text is empty or not
#     if not context_text:
#         context_text = "No relevant context found."  # Handle empty case

#     chain = (
#         {"context": context_text, "query": user_question}  # Provide the context as text
#         | prompt
#         | llm
#         | output_parser
#     )

#     return chain.invoke({"context": context_text, "query": user_question})  # Ensure both are strings
