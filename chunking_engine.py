"""
Chunking Engine Module
Adapted from docs/chunk-logic.md with improved regex and structured output.
Returns List[dict] objects for each day entry.
"""

import re
from typing import List, Dict


# Improved regex pattern as specified in project plan
DAY_RE = re.compile(r'^\s*Day\s+(\d+)\b.*', re.I)


def parse_journal_entries(text: str) -> List[Dict]:
    """
    Parse a journal document into individual day entries.
    Adapted from docs/chunk-logic.md with improved regex and structured output.
    
    Args:
        text (str): The full journal text
        
    Returns:
        List[Dict]: List of dictionaries with {"day": int, "text": str} format
    """
    
    entries = []
    current_day = None
    current_content = []
    
    lines = text.split('\n')
    
    for line in lines:
        # Check if this line matches the improved "Day X" pattern
        match = DAY_RE.match(line)
        
        if match:
            # If we were already processing a day, save it
            if current_day is not None:
                entry_text = '\n'.join(current_content).strip()
                if entry_text:  # Only add non-empty entries
                    entries.append({
                        "day": current_day,
                        "text": entry_text
                    })
            
            # Start processing the new day
            current_day = int(match.group(1))
            current_content = [line]  # Include the "Day X" line (full_entry_with_header)
        else:
            # Add this line to the current day's content
            if current_day is not None:
                current_content.append(line)
    
    # Don't forget the last entry
    if current_day is not None:
        entry_text = '\n'.join(current_content).strip()
        if entry_text:  # Only add non-empty entries
            entries.append({
                "day": current_day,
                "text": entry_text
            })
    
    return entries


def chunk_by_paragraphs(text: str, paragraphs_per_chunk: int = 3) -> List[Dict]:
    """
    Parse document into chunks based on paragraph count.
    
    Args:
        text (str): The full document text
        paragraphs_per_chunk (int): Number of paragraphs per chunk
        
    Returns:
        List[Dict]: List of dictionaries with {"day": int, "text": str} format
                   (where "day" is actually chunk number for consistency)
    """
    if not text.strip():
        return []
    
    # Split text into paragraphs (separated by blank lines)
    paragraphs = []
    current_paragraph = []
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if line:  # Non-empty line
            current_paragraph.append(line)
        else:  # Empty line - end current paragraph
            if current_paragraph:
                paragraph_text = ' '.join(current_paragraph)
                paragraphs.append(paragraph_text)
                current_paragraph = []
    
    # Add final paragraph if exists
    if current_paragraph:
        paragraph_text = ' '.join(current_paragraph)
        paragraphs.append(paragraph_text)
    
    # Group paragraphs into chunks
    chunks = []
    chunk_number = 1
    
    for i in range(0, len(paragraphs), paragraphs_per_chunk):
        chunk_paragraphs = paragraphs[i:i + paragraphs_per_chunk]
        chunk_text = '\n\n'.join(chunk_paragraphs)
        
        if chunk_text.strip():
            chunks.append({
                "day": chunk_number,  # Using "day" for consistency with existing code
                "text": chunk_text
            })
            chunk_number += 1
    
    return chunks


def chunk_document_text(text: str, method: str = "daily", paragraphs_per_chunk: int = 3) -> List[Dict]:
    """
    Main chunking function that processes extracted document text.
    
    Args:
        text (str): Raw text extracted from document
        method (str): Chunking method - "daily" or "paragraph"
        paragraphs_per_chunk (int): Number of paragraphs per chunk (for paragraph method)
        
    Returns:
        List[Dict]: List of entries with {"day": int, "text": str} format
    """
    if method == "paragraph":
        return chunk_by_paragraphs(text, paragraphs_per_chunk)
    else:  # Default to daily journal entry method
        return parse_journal_entries(text)


def get_chunk_count(chunks: List[Dict]) -> int:
    """
    Get the number of chunks for logging purposes.
    
    Args:
        chunks (List[Dict]): List of day entry chunks
        
    Returns:
        int: Number of chunks
    """
    return len(chunks)


def get_chunk_summary(chunks: List[Dict], method: str = "daily") -> str:
    """
    Get a summary string of chunks for display purposes.
    
    Args:
        chunks (List[Dict]): List of entry chunks
        method (str): Chunking method used - "daily" or "paragraph"
        
    Returns:
        str: Summary string like "5 entries (Days 1-5)" or "5 chunks"
    """
    if not chunks:
        return "No entries found"
    
    count = len(chunks)
    
    if method == "paragraph":
        if count == 1:
            return f"1 chunk"
        else:
            return f"{count} chunks"
    else:  # Daily journal method
        days = [chunk["day"] for chunk in chunks]
        min_day = min(days)
        max_day = max(days)
        
        if count == 1:
            return f"1 entry (Day {min_day})"
        elif min_day == max_day:
            return f"{count} entries (Day {min_day})"
        else:
            return f"{count} entries (Days {min_day}-{max_day})"


# Test function for debugging
def test_chunking_with_sample():
    """
    Test function using sample text for both chunking methods.
    """
    sample_text = """Day 1

Today I woke up feeling energized and ready to tackle the world. The morning sun streamed through my bedroom window.

Day 2

Had an interesting conversation with my neighbor Mrs. Johnson today. She told me about her garden.

Day 3

Spent the afternoon reading in the park. Found a quiet spot under an old oak tree."""
    
    print("=== Testing Daily Journal Chunking ===")
    daily_chunks = chunk_document_text(sample_text, method="daily")
    print(f"Found {get_chunk_count(daily_chunks)} chunks:")
    print(f"Summary: {get_chunk_summary(daily_chunks, method='daily')}")
    
    for chunk in daily_chunks:
        print(f"\n--- Day {chunk['day']} ---")
        print(chunk['text'][:100] + "..." if len(chunk['text']) > 100 else chunk['text'])
    
    print("\n\n=== Testing Paragraph Chunking (2 paragraphs per chunk) ===")
    paragraph_chunks = chunk_document_text(sample_text, method="paragraph", paragraphs_per_chunk=2)
    print(f"Found {get_chunk_count(paragraph_chunks)} chunks:")
    print(f"Summary: {get_chunk_summary(paragraph_chunks, method='paragraph')}")
    
    for chunk in paragraph_chunks:
        print(f"\n--- Chunk {chunk['day']} ---")
        print(chunk['text'][:100] + "..." if len(chunk['text']) > 100 else chunk['text'])
    
    return daily_chunks, paragraph_chunks


if __name__ == "__main__":
    # Run test when script is executed directly
    test_chunking_with_sample() 