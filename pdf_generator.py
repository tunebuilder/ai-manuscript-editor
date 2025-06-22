"""
PDF Generator Module
Re-assembly & Export functionality using ReportLab.
Concatenates edited chunks and generates downloadable PDF.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from typing import List, Dict
import io
from datetime import datetime


def concatenate_chunks(chunks: List[Dict]) -> str:
    """
    Concatenate edited chunks with two blank lines between days.
    
    Args:
        chunks (List[Dict]): List of edited chunks with {"day": int, "text": str}
        
    Returns:
        str: Concatenated text with proper spacing
    """
    if not chunks:
        return ""
    
    # Sort chunks by day number to ensure proper order
    sorted_chunks = sorted(chunks, key=lambda x: x["day"])
    
    # Concatenate with two blank lines between days
    full_text_parts = []
    
    for chunk in sorted_chunks:
        chunk_text = chunk["text"].strip()
        if chunk_text:
            full_text_parts.append(chunk_text)
    
    # Join with two blank lines (two \n\n creates the spacing)
    full_text = "\n\n\n\n".join(full_text_parts)
    
    return full_text


def create_pdf_bytes(chunks: List[Dict], title: str = "Enhanced Journal") -> bytes:
    """
    Create a PDF from edited chunks using ReportLab.
    Returns in-memory bytes for download (no disk I/O).
    
    Args:
        chunks (List[Dict]): List of edited chunks
        title (str): Title for the PDF document
        
    Returns:
        bytes: PDF content as bytes
    """
    # Create in-memory buffer
    buffer = io.BytesIO()
    
    # Create PDF document with A4 portrait format
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1*inch,
        bottomMargin=1*inch,
        leftMargin=1*inch,
        rightMargin=1*inch
    )
    
    # Get sample styles and create custom styles
    styles = getSampleStyleSheet()
    
    # Custom title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor='black'
    )
    
    # Custom day header style
    day_header_style = ParagraphStyle(
        'DayHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=24,
        alignment=TA_LEFT,
        textColor='black'
    )
    
    # Custom body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_LEFT,
        textColor='black',
        leading=16  # Line spacing
    )
    
    # Build the story (content for PDF)
    story = []
    
    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    # Add generation date
    date_str = datetime.now().strftime("%B %d, %Y")
    date_para = Paragraph(f"Generated on {date_str}", styles['Normal'])
    story.append(date_para)
    story.append(Spacer(1, 30))
    
    # Sort chunks by day number
    sorted_chunks = sorted(chunks, key=lambda x: x["day"])
    
    # Add each chunk to the story
    for i, chunk in enumerate(sorted_chunks):
        chunk_text = chunk["text"].strip()
        
        if chunk_text:
            # Split chunk into lines
            lines = chunk_text.split('\n')
            
            # Look for day header (first line starting with "Day")
            day_header = None
            content_lines = []
            
            for line in lines:
                if line.strip().startswith('Day ') and day_header is None:
                    day_header = line.strip()
                else:
                    content_lines.append(line)
            
            # Add day header if found
            if day_header:
                story.append(Paragraph(day_header, day_header_style))
            
            # Add content paragraphs
            current_paragraph = []
            for line in content_lines:
                line = line.strip()
                if line:  # Non-empty line
                    current_paragraph.append(line)
                else:  # Empty line - end current paragraph
                    if current_paragraph:
                        para_text = ' '.join(current_paragraph)
                        # Escape special characters for ReportLab
                        para_text = para_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(para_text, body_style))
                        current_paragraph = []
            
            # Add final paragraph if exists
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                para_text = para_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(para_text, body_style))
            
            # Add spacing between days (except for last chunk)
            if i < len(sorted_chunks) - 1:
                story.append(Spacer(1, 24))  # Two blank lines equivalent
    
    # Build PDF
    doc.build(story)
    
    # Get PDF bytes
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def get_pdf_filename(chunks: List[Dict]) -> str:
    """
    Generate a filename for the PDF based on content.
    
    Args:
        chunks (List[Dict]): List of chunks
        
    Returns:
        str: Suggested filename
    """
    if not chunks:
        return "enhanced_journal.pdf"
    
    # Sort chunks to get day range
    sorted_chunks = sorted(chunks, key=lambda x: x["day"])
    first_day = sorted_chunks[0]["day"]
    last_day = sorted_chunks[-1]["day"]
    
    if first_day == last_day:
        return f"enhanced_journal_day_{first_day}.pdf"
    else:
        return f"enhanced_journal_days_{first_day}-{last_day}.pdf"


def get_pdf_stats(chunks: List[Dict]) -> Dict[str, any]:
    """
    Get statistics about the PDF that will be generated.
    
    Args:
        chunks (List[Dict]): List of chunks
        
    Returns:
        Dict: Statistics about the PDF
    """
    if not chunks:
        return {"entries": 0, "words": 0, "characters": 0}
    
    total_words = 0
    total_chars = 0
    
    for chunk in chunks:
        text = chunk["text"]
        words = len(text.split())
        chars = len(text)
        
        total_words += words
        total_chars += chars
    
    return {
        "entries": len(chunks),
        "words": total_words,
        "characters": total_chars,
        "estimated_pages": max(1, total_words // 250)  # Rough estimate: 250 words per page
    }


# Test function for debugging
def test_pdf_generation():
    """
    Test function to create a sample PDF.
    """
    sample_chunks = [
        {
            "day": 1,
            "text": "Day 1\n\nToday I embarked on a journey of discovery. The morning light filtered through ancient oak leaves, casting dancing shadows on the forest floor. Each step forward revealed new wonders."
        },
        {
            "day": 2,  
            "text": "Day 2\n\nConversations with strangers often yield the most profound insights. Mrs. Henderson, the village baker, shared stories of her grandmother's recipes—each one a bridge between generations."
        }
    ]
    
    try:
        # Generate PDF
        pdf_bytes = create_pdf_bytes(sample_chunks, "Test Enhanced Journal")
        
        # Get stats
        stats = get_pdf_stats(sample_chunks)
        
        print(f"PDF generated successfully!")
        print(f"Size: {len(pdf_bytes)} bytes")
        print(f"Stats: {stats}")
        
        # Save to file for testing
        with open("test_output.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("Test PDF saved as 'test_output.pdf'")
        
        return pdf_bytes
        
    except Exception as e:
        print(f"PDF generation failed: {str(e)}")
        return None


if __name__ == "__main__":
    # Run test when script is executed directly
    test_pdf_generation() 