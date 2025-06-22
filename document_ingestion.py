"""
Document Ingestion Module
Extracts text from PDF and DOCX files while preserving line breaks.
"""

import PyPDF2
from docx import Document
from typing import Tuple, Optional
import io


def detect_file_type(filename: str) -> str:
    """
    Detect file type based on extension.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        str: File type ('pdf', 'docx', or 'unknown')
    """
    filename_lower = filename.lower()
    if filename_lower.endswith('.pdf'):
        return 'pdf'
    elif filename_lower.endswith('.docx'):
        return 'docx'
    else:
        return 'unknown'


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, bool]:
    """
    Extract text from PDF file bytes, preserving line breaks.
    
    Args:
        file_bytes (bytes): PDF file content as bytes
        
    Returns:
        Tuple[str, bool]: (extracted_text, success_flag)
    """
    try:
        # Create a BytesIO object from the bytes
        pdf_file = io.BytesIO(file_bytes)
        
        # Create PDF reader
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text_content = []
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            
            # Add page text, preserving line breaks
            if page_text.strip():
                text_content.append(page_text)
        
        # Join pages with double line breaks
        full_text = '\n\n'.join(text_content)
        
        return full_text, True
        
    except Exception as e:
        print(f"Error extracting PDF text: {str(e)}")
        return "", False


def extract_text_from_docx(file_bytes: bytes) -> Tuple[str, bool]:
    """
    Extract text from DOCX file bytes, preserving line breaks.
    
    Args:
        file_bytes (bytes): DOCX file content as bytes
        
    Returns:
        Tuple[str, bool]: (extracted_text, success_flag)
    """
    try:
        # Create a BytesIO object from the bytes
        docx_file = io.BytesIO(file_bytes)
        
        # Create Document object
        doc = Document(docx_file)
        
        # Extract text from all paragraphs
        text_content = []
        
        for paragraph in doc.paragraphs:
            # Add paragraph text, preserving original line structure
            para_text = paragraph.text
            if para_text.strip():  # Only add non-empty paragraphs
                text_content.append(para_text)
        
        # Join paragraphs with single line breaks to preserve structure
        full_text = '\n'.join(text_content)
        
        return full_text, True
        
    except Exception as e:
        print(f"Error extracting DOCX text: {str(e)}")
        return "", False


def extract_document_text(file_bytes: bytes, filename: str) -> Tuple[str, bool, str]:
    """
    Extract text from document based on file type.
    
    Args:
        file_bytes (bytes): File content as bytes
        filename (str): Name of the file
        
    Returns:
        Tuple[str, bool, str]: (extracted_text, success_flag, file_type)
    """
    file_type = detect_file_type(filename)
    
    if file_type == 'pdf':
        text, success = extract_text_from_pdf(file_bytes)
        return text, success, file_type
    elif file_type == 'docx':
        text, success = extract_text_from_docx(file_bytes)
        return text, success, file_type
    else:
        return "", False, file_type


# Utility function for testing
def extract_document_from_path(file_path: str) -> Tuple[str, bool, str]:
    """
    Extract text from document file path (for testing purposes).
    
    Args:
        file_path (str): Path to the document file
        
    Returns:
        Tuple[str, bool, str]: (extracted_text, success_flag, file_type)
    """
    try:
        with open(file_path, 'rb') as file:
            file_bytes = file.read()
            return extract_document_text(file_bytes, file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return "", False, "unknown" 