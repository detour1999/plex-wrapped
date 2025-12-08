# ABOUTME: Shared utility functions used across the plex-wrapped codebase.
# ABOUTME: Includes text processing and common helpers.

import re


def slugify(text: str) -> str:
    """Convert text to a safe filename slug.

    Removes special characters, converts to lowercase, replaces spaces with hyphens,
    and limits the result to 50 characters.

    Args:
        text: Input text to slugify

    Returns:
        Slugified string safe for use in filenames and URLs

    Examples:
        >>> slugify("The Beatles")
        'the-beatles'
        >>> slugify("AC/DC - Highway to Hell!")
        'acdc-highway-to-hell'
    """
    if not text:
        return ""

    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces and multiple hyphens with single hyphen
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    # Limit length
    return text[:50]
