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
