import os
import tempfile
import streamlit as st
from PyPDF2 import PdfReader
import docx  # python-docx for .docx files

class DocumentProcessor:
    """Class for processing uploaded documents to extract text content."""
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file given its file path."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, docx_path):
        """Extract text from a Word (.docx or .doc) file given its file path."""
        try:
            doc = docx.Document(docx_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            st.error(f"Error extracting text from Word document: {e}")
            return ""
    
    def extract_text_from_txt(self, txt_file):
        """Extract text from an uploaded plain text file (BytesIO)."""
        try:
            text_bytes = txt_file.read()
            text = text_bytes.decode('utf-8', errors='ignore')
            return text
        except Exception as e:
            st.error(f"Error extracting text from text file: {e}")
            return ""
    
    def process_document(self, uploaded_file):
        """
        Process an uploaded file and return its text content.
        Supports PDF (.pdf), Word (.docx, .doc), and plain text (.txt) files.
        """
        if uploaded_file is None:
            return ""
        # Save the uploaded file to a temporary file on disk
        suffix = f".{uploaded_file.name.split('.')[-1]}"
        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_file_path = tmp.name
            # Determine file type and extract text accordingly
            ext = uploaded_file.name.split('.')[-1].lower()
            if ext == 'pdf':
                text = self.extract_text_from_pdf(tmp_file_path)
            elif ext in ['docx', 'doc']:
                text = self.extract_text_from_docx(tmp_file_path)
            elif ext == 'txt':
                # For text files, we can read directly from the uploaded file bytes
                text = self.extract_text_from_txt(uploaded_file)
            else:
                st.error(f"Unsupported file format: {ext}")
                text = ""
            return text
        finally:
            # Clean up the temporary file
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
