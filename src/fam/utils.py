import re


COL_END = "\033[0m"
COL_RED = "\033[91m"
COL_GREEN = "\033[92m"
COL_YELLOW = "\033[93m"
COL_BLUE = "\033[94m"
COL_MAGENTA = "\033[95m"
COL_CYAN = "\033[96m"


def pos_to_line_col(src_code: str, pos: int) -> tuple[int, int]:
    """Accepts source code and a character position, and returns
    a line and column (x, y), where x and y are line and column (0-based)."""

    current_pos = 0

    src_lines = src_code.splitlines()

    for line_num, line_content in enumerate(src_lines):
        line_len = len(line_content)

        # include newline that was removed by splitlines()
        # splitlines() makes sure that source code buffers
        # are stored as lists like ['line1', 'line2', etc.]
        # without the newlines
        total_len = line_len + 1  # for '\n'

        if current_pos <= pos < current_pos + total_len:
            col = pos - current_pos
            return line_num, col

        current_pos += total_len

    return len(src_lines), 0


def unescape_string(s: str) -> str:
    """Unescape escape sequences in a string literal and remove the string's surrounding quotes."""

    # Remove surrounding quotes
    content = s[1:-1]

    # Handle common escape sequences
    SEQUENCES = [
        ('\\n', '\n'),
        ('\\t', '\t'),
        ('\\r', '\r'),
        ('\\"', '"'),
        ('\\\\', '\\'),
    ]

    for seq in SEQUENCES:
        content = content.replace(seq[0], seq[1])

    # Handle escapes like "\xHH" for hex values
    def replace_hex(match: re.Match) -> str:
        return chr(int(match.group(1), 16))
    return re.sub(r'\\x([0-9a-fA-F]{2})', replace_hex, content)
