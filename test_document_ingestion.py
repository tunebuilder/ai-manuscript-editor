"""
Unit tests for document ingestion module.
Tests both PDF and DOCX extractors with 1-2 page fixtures.
"""

import unittest
import os
from document_ingestion import (
    detect_file_type,
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_document_text,
    extract_document_from_path
)


class TestDocumentIngestion(unittest.TestCase):
    """Test cases for document ingestion functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        # Ensure test fixtures exist
        cls.test_pdf_path = 'test_fixtures/sample_journal.pdf'
        cls.test_docx_path = 'test_fixtures/sample_journal.docx'
        cls.test_txt_path = 'test_fixtures/sample_journal.txt'
        
        # Read expected content
        if os.path.exists(cls.test_txt_path):
            with open(cls.test_txt_path, 'r', encoding='utf-8') as f:
                cls.expected_content = f.read()
        else:
            cls.expected_content = ""
    
    def test_detect_file_type_pdf(self):
        """Test file type detection for PDF files."""
        self.assertEqual(detect_file_type('document.pdf'), 'pdf')
        self.assertEqual(detect_file_type('Document.PDF'), 'pdf')
        self.assertEqual(detect_file_type('my_file.pdf'), 'pdf')
    
    def test_detect_file_type_docx(self):
        """Test file type detection for DOCX files."""
        self.assertEqual(detect_file_type('document.docx'), 'docx')
        self.assertEqual(detect_file_type('Document.DOCX'), 'docx')
        self.assertEqual(detect_file_type('my_file.docx'), 'docx')
    
    def test_detect_file_type_unknown(self):
        """Test file type detection for unknown files."""
        self.assertEqual(detect_file_type('document.txt'), 'unknown')
        self.assertEqual(detect_file_type('file.doc'), 'unknown')
        self.assertEqual(detect_file_type('image.jpg'), 'unknown')
    
    def test_extract_pdf_from_path(self):
        """Test PDF text extraction from file path."""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test fixture {self.test_pdf_path} not found. Run create_test_fixtures.py first.")
        
        text, success, file_type = extract_document_from_path(self.test_pdf_path)
        
        self.assertTrue(success, "PDF extraction should succeed")
        self.assertEqual(file_type, 'pdf', "File type should be detected as PDF")
        self.assertIsInstance(text, str, "Extracted text should be a string")
        self.assertGreater(len(text), 0, "Extracted text should not be empty")
        
        # Check for key content
        self.assertIn("Day 1", text, "Should contain Day 1 header")
        self.assertIn("Day 2", text, "Should contain Day 2 header")
        self.assertIn("Day 3", text, "Should contain Day 3 header")
    
    def test_extract_docx_from_path(self):
        """Test DOCX text extraction from file path."""
        if not os.path.exists(self.test_docx_path):
            self.skipTest(f"Test fixture {self.test_docx_path} not found. Run create_test_fixtures.py first.")
        
        text, success, file_type = extract_document_from_path(self.test_docx_path)
        
        self.assertTrue(success, "DOCX extraction should succeed")
        self.assertEqual(file_type, 'docx', "File type should be detected as DOCX")
        self.assertIsInstance(text, str, "Extracted text should be a string")
        self.assertGreater(len(text), 0, "Extracted text should not be empty")
        
        # Check for key content
        self.assertIn("Day 1", text, "Should contain Day 1 header")
        self.assertIn("Day 2", text, "Should contain Day 2 header")
        self.assertIn("Day 3", text, "Should contain Day 3 header")
    
    def test_extract_pdf_bytes(self):
        """Test PDF text extraction from bytes."""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test fixture {self.test_pdf_path} not found. Run create_test_fixtures.py first.")
        
        # Read PDF as bytes
        with open(self.test_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        text, success = extract_text_from_pdf(pdf_bytes)
        
        self.assertTrue(success, "PDF bytes extraction should succeed")
        self.assertIsInstance(text, str, "Extracted text should be a string")
        self.assertGreater(len(text), 0, "Extracted text should not be empty")
    
    def test_extract_docx_bytes(self):
        """Test DOCX text extraction from bytes."""
        if not os.path.exists(self.test_docx_path):
            self.skipTest(f"Test fixture {self.test_docx_path} not found. Run create_test_fixtures.py first.")
        
        # Read DOCX as bytes
        with open(self.test_docx_path, 'rb') as f:
            docx_bytes = f.read()
        
        text, success = extract_text_from_docx(docx_bytes)
        
        self.assertTrue(success, "DOCX bytes extraction should succeed")
        self.assertIsInstance(text, str, "Extracted text should be a string")
        self.assertGreater(len(text), 0, "Extracted text should not be empty")
    
    def test_extract_document_text_integration(self):
        """Test the main extract_document_text function."""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test fixture {self.test_pdf_path} not found. Run create_test_fixtures.py first.")
        
        # Test with PDF
        with open(self.test_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        text, success, file_type = extract_document_text(pdf_bytes, 'test.pdf')
        
        self.assertTrue(success, "PDF document extraction should succeed")
        self.assertEqual(file_type, 'pdf', "Should detect PDF file type")
        self.assertGreater(len(text), 0, "Should extract text content")
    
    def test_line_break_preservation(self):
        """Test that line breaks are preserved in extracted text."""
        if not os.path.exists(self.test_docx_path):
            self.skipTest(f"Test fixture {self.test_docx_path} not found. Run create_test_fixtures.py first.")
        
        text, success, file_type = extract_document_from_path(self.test_docx_path)
        
        self.assertTrue(success, "DOCX extraction should succeed")
        
        # Check that text contains line breaks
        self.assertIn('\n', text, "Extracted text should contain line breaks")
        
        # Split into lines and check structure
        lines = text.split('\n')
        self.assertGreater(len(lines), 1, "Should have multiple lines")
    
    def test_invalid_file_handling(self):
        """Test handling of invalid or non-existent files."""
        # Test non-existent file
        text, success, file_type = extract_document_from_path('nonexistent.pdf')
        self.assertFalse(success, "Should fail for non-existent file")
        self.assertEqual(text, "", "Should return empty string for failed extraction")
        
        # Test invalid bytes
        text, success = extract_text_from_pdf(b"invalid pdf content")
        self.assertFalse(success, "Should fail for invalid PDF bytes")
        
        text, success = extract_text_from_docx(b"invalid docx content")
        self.assertFalse(success, "Should fail for invalid DOCX bytes")


if __name__ == '__main__':
    print("Running document ingestion tests...")
    print("Note: If tests are skipped, run 'python create_test_fixtures.py' first to generate test files.")
    
    unittest.main(verbosity=2) 