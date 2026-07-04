import re

SHORT_LIMIT = 1000
MEDIUM_LIMIT = 10000


def format_response(text: str) -> str:
    """Format opencode output for WhatsApp display."""
    if not text:
        return "No response"

    # Remove ANSI codes
    text = strip_ansi(text)

    # Format code blocks for WhatsApp readability
    text = format_code_blocks(text)

    # Truncate based on length
    if len(text) <= SHORT_LIMIT:
        return text
    elif len(text) <= MEDIUM_LIMIT:
        return text + "\n\n_Response truncated. Reply with 'read more' for full output._"
    else:
        return text[:MEDIUM_LIMIT] + "\n\n...\n_Response too long. Full output saved to server._"


def format_code_blocks(text: str) -> str:
    """Ensure code blocks are properly formatted for WhatsApp."""
    # Ensure opening ```
    text = re.sub(r'(?<!`)```(?!`)', '```', text)
    return text


def strip_ansi(text: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
