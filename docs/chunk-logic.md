import re
from typing import Dict

def parse_journal_entries(text: str) -> Dict[int, str]:
    """
    Parse a journal document into individual day entries.
    
    Args:
        text (str): The full journal text
        
    Returns:
        Dict[int, str]: Dictionary with day numbers as keys and full entries as values
    """
    
    # This regex looks for "Day" followed by a space and one or more digits
    day_pattern = r'^Day (\d+)

    
    entries = {}
    current_day = None
    current_content = []
    
    lines = text.split('\n')
    
    for line in lines:
        # Check if this line matches the "Day X" pattern
        match = re.match(day_pattern, line.strip())
        
        if match:
            # If we were already processing a day, save it
            if current_day is not None:
                entries[current_day] = '\n'.join(current_content).strip()
            
            # Start processing the new day
            current_day = int(match.group(1))
            current_content = [line]  # Include the "Day X" line
        else:
            # Add this line to the current day's content
            if current_day is not None:
                current_content.append(line)
    
    # Don't forget the last entry
    if current_day is not None:
        entries[current_day] = '\n'.join(current_content).strip()
    
    return entries

def parse_journal_from_file(filename: str) -> Dict[int, str]:
    """
    Parse journal entries from a file.
    
    Args:
        filename (str): Path to the journal file
        
    Returns:
        Dict[int, str]: Dictionary with day numbers as keys and full entries as values
    """
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()
    
    return parse_journal_entries(text)