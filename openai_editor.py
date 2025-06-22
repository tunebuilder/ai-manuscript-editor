"""
OpenAI Editor Module
Batched editing via OpenAI API using gpt-4.5-preview model.
Reads system prompt from docs/openai-api.md at runtime.
"""

import os
import time
import json
from typing import List, Dict, Tuple
from openai import OpenAI
import streamlit as st


def load_system_prompt() -> str:
    """
    Load system prompt from docs/openai-api.md at runtime.
    
    Returns:
        str: System prompt text
    """
    try:
        with open('docs/openai-api.md', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract the system prompt from the content field
        # Looking for the text content in the system message
        lines = content.split('\n')
        in_system_content = False
        system_prompt_lines = []
        
        for line in lines:
            if '"text":' in line and 'You are a stylistic editor' in line:
                # Extract the text content between quotes
                start_quote = line.find('"You are a stylistic editor')
                if start_quote != -1:
                    # Find the end of this text block
                    text_content = line[start_quote+1:]  # Remove first quote
                    # Remove trailing quote and comma if present
                    if text_content.endswith('",'):
                        text_content = text_content[:-2]
                    elif text_content.endswith('"'):
                        text_content = text_content[:-1]
                    
                    # Replace escaped newlines with actual newlines
                    text_content = text_content.replace('\\n', '\n')
                    return text_content
        
        # Fallback: extract from the full content if parsing fails
        return """You are a stylistic editor focused on rhythm and tone, and the creation of polished work worthy of a reader's interest and time.  
TASK: Enhance narrative energy without altering structure.

Rules
1. Avoid adverbs, they're not your friends. Especially after: "he said" or "she said".
2. Don't use passive voice.
3. Don't obsess over perfect grammar. The object of fiction isn't grammatical correctness… but to make the reader welcome and then tell a story.  
4. Replace clichés with fresher language; strengthen verbs and imagery. Then reread that new sentence to confirm that the new version has more literary usefulness. If not, do not make the change.
5. Maintain paragraph order but may insert brief transitional phrases (<12 words) for flow.
4. Preserve the author's point of view, tense, and factual statements but using a prose style and grammatical pattern of the best modern writers.
5. Journal-day headers stay intact except for mechanical fixes.
6. Return EDITED TEXT only—no editor notes or tags."""
        
    except Exception as e:
        st.error(f"Error loading system prompt: {str(e)}")
        return "You are a helpful assistant that edits text."


def create_openai_client() -> OpenAI:
    """
    Create OpenAI client using API key from environment.
    
    Returns:
        OpenAI: Configured OpenAI client
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    return OpenAI(api_key=api_key)


def edit_single_chunk(client: OpenAI, system_prompt: str, chunk_text: str) -> Tuple[str, bool]:
    """
    Edit a single chunk using OpenAI API.
    
    Args:
        client (OpenAI): OpenAI client
        system_prompt (str): System prompt for editing
        chunk_text (str): Text to edit
        
    Returns:
        Tuple[str, bool]: (edited_text, success_flag)
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.5-preview",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": chunk_text
                }
            ],
            temperature=0.43,
            max_completion_tokens=16384,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        edited_text = response.choices[0].message.content
        return edited_text, True
        
    except Exception as e:
        print(f"Error editing chunk: {str(e)}")
        return chunk_text, False  # Return original text on error


def edit_batch_with_retry(client: OpenAI, system_prompt: str, batch_chunks: List[Dict], max_retries: int = 3) -> List[Dict]:
    """
    Edit a batch of chunks with exponential backoff retry logic.
    
    Args:
        client (OpenAI): OpenAI client
        system_prompt (str): System prompt for editing
        batch_chunks (List[Dict]): List of chunks to edit
        max_retries (int): Maximum number of retries
        
    Returns:
        List[Dict]: List of edited chunks with {"day": int, "text": str, "edited": bool}
    """
    edited_chunks = []
    
    for chunk in batch_chunks:
        chunk_text = chunk["text"]
        day_num = chunk["day"]
        
        success = False
        edited_text = chunk_text
        
        for attempt in range(max_retries + 1):
            try:
                edited_text, success = edit_single_chunk(client, system_prompt, chunk_text)
                if success:
                    break
                    
            except Exception as e:
                if attempt < max_retries:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    print(f"Retry {attempt + 1} for Day {day_num} in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to edit Day {day_num} after {max_retries} retries")
        
        edited_chunks.append({
            "day": day_num,
            "text": edited_text,
            "edited": success
        })
    
    return edited_chunks


def process_chunks_in_batches(chunks: List[Dict], system_prompt: str = None, progress_callback=None) -> List[Dict]:
    """
    Process all chunks in batches of 4 with OpenAI editing.
    
    Args:
        chunks (List[Dict]): List of chunks to edit
        system_prompt (str): Custom system prompt to use (if None, loads default)
        progress_callback: Optional callback function for progress updates
        
    Returns:
        List[Dict]: List of edited chunks
    """
    if not chunks:
        return []
    
    # Use provided system prompt or load default
    if system_prompt is None:
        system_prompt = load_system_prompt()
    
    # Create OpenAI client
    client = create_openai_client()
    
    # Process in batches of 4
    batch_size = 4
    total_chunks = len(chunks)
    all_edited_chunks = []
    
    for i in range(0, total_chunks, batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_chunks + batch_size - 1) // batch_size
        
        if progress_callback:
            # Enhanced batch status message as specified in project plan: "Sending batch 3/10 …"
            progress_callback(f"Sending batch {batch_num}/{total_batches} …")
        
        # Edit this batch
        edited_batch = edit_batch_with_retry(client, system_prompt, batch_chunks)
        all_edited_chunks.extend(edited_batch)
    
    return all_edited_chunks


def get_editing_stats(edited_chunks: List[Dict]) -> Dict[str, int]:
    """
    Get statistics about the editing process.
    
    Args:
        edited_chunks (List[Dict]): List of edited chunks
        
    Returns:
        Dict[str, int]: Statistics dictionary
    """
    total = len(edited_chunks)
    successful = sum(1 for chunk in edited_chunks if chunk.get("edited", False))
    failed = total - successful
    
    return {
        "total": total,
        "successful": successful,
        "failed": failed
    }


# Test function for debugging
def test_editing_with_sample():
    """
    Test function using sample journal chunks.
    """
    sample_chunks = [
        {
            "day": 1,
            "text": "Day 1\n\nToday I woke up feeling energized and ready to tackle the world. The morning sun was shining brightly through my bedroom window."
        },
        {
            "day": 2,
            "text": "Day 2\n\nI had an interesting conversation with my neighbor Mrs. Johnson today. She told me about her garden and how she talks to her tomatoes."
        }
    ]
    
    try:
        edited_chunks = process_chunks_in_batches(sample_chunks, system_prompt=None)
        stats = get_editing_stats(edited_chunks)
        
        print(f"Editing complete: {stats['successful']}/{stats['total']} successful")
        
        for chunk in edited_chunks:
            print(f"\n--- Day {chunk['day']} {'(Edited)' if chunk['edited'] else '(Failed)'} ---")
            print(chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text'])
        
        return edited_chunks
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return []


if __name__ == "__main__":
    # Run test when script is executed directly
    test_editing_with_sample() 