import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Union


class Colors:
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7


def beautify_filename(filename: str) -> str:
    """Beautify filename by removing extension, capitalizing, and replacing -/_ with spaces"""
    name = Path(filename).stem
    name = name.replace('-', ' ').replace('_', ' ')
    name = ' '.join(word.capitalize() for word in name.split())
    return name


def fuzzy_match(query: str, text: str) -> Tuple[bool, float]:
    """
    Perform fuzzy matching between query and text.
    Returns (matched, score) where score is lower for better matches.
    
    The algorithm finds all characters of query in text in order,
    and scores based on how compact the match is.
    """
    query = query.lower()
    text = text.lower()
    
    if not query:
        return True, 0.0
    
    text_pos = 0
    score = 0.0
    
    for char in query:
        found_pos = text.find(char, text_pos)
        if found_pos == -1:
            return False, float('inf')
        
        distance = found_pos - text_pos
        score += distance
        text_pos = found_pos + 1
    
    return True, score


def fuzzy_filter(items: List[Dict[str, Any]], query: str, search_field: str = "summary") -> List[Dict[str, Any]]:
    """
    Filter items by fuzzy matching on a specific field.
    Returns items sorted by match quality.
    """
    if not query:
        return items
    
    matches = []
    for item in items:
        field_value = str(item.get(search_field, ""))
        matched, score = fuzzy_match(query, field_value)
        if matched:
            matches.append((item, score))
    
    matches.sort(key=lambda x: x[1])
    return [item for item, score in matches]


def sanitize_display_string(text: str, max_length: Union[int, None] = None) -> str:
    """
    Sanitize a string for curses display by:
    1. Replacing newlines and other control characters with spaces
    2. Collapsing multiple spaces into single spaces
    3. Truncating to max_length if specified
    4. Stripping leading/trailing whitespace
    """
    if not text:
        return ""

    text = str(text)

    sanitized = ''.join(
        ' ' if ord(c) < 32 else c
        for c in text
    )

    sanitized = re.sub(r'\s+', ' ', sanitized)
    sanitized = sanitized.strip()

    if max_length is not None and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized
