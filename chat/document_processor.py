import os
from typing import List
import tempfile

# Document loading
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Embeddings and vectorstore
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


def load_document(file_path: str):
    """
    Load a document based on its file extension.

    Args:
        file_path: Path to the document

    Returns:
        List of Document objects
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".pdf":
        loader = PyPDFLoader(file_path)
    elif file_extension == ".docx":
        loader = Docx2txtLoader(file_path)
    elif file_extension == ".txt":
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

    return loader.load()


def split_documents(documents):
    """
    Split documents into chunks for better processing.

    Args:
        documents: List of Document objects

    Returns:
        List of document chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    return text_splitter.split_documents(documents)


def process_documents(file_paths: List[str]):
    """
    Process multiple documents and create a FAISS vectorstore.

    Args:
        file_paths: List of file paths to process

    Returns:
        FAISS vectorstore
    """
    # Load all documents
    documents = []
    for file_path in file_paths:
        try:
            documents.extend(load_document(file_path))
        except Exception as e:
            raise Exception(f"Error loading {file_path}: {str(e)}")

    # Split documents into chunks
    document_chunks = split_documents(documents)

    if not document_chunks:
        raise ValueError("No document content found or documents could not be processed")

    # Initialize embeddings model
    embeddings = OpenAIEmbeddings()

    # Create vectorstore
    vectorstore = FAISS.from_documents(document_chunks, embeddings)

    return vectorstore
