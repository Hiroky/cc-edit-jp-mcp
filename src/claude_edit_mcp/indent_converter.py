"""Utility module for converting between tabs and spaces for indent normalization."""


def tabs_to_spaces(content: str, spaces: int = 4) -> str:
    """
    Convert tabs to spaces in content.
    
    Args:
        content: The content to convert
        spaces: Number of spaces per tab (default: 4)
    
    Returns:
        Content with tabs converted to spaces
    """
    return content.replace('\t', ' ' * spaces)


def spaces_to_tabs(content: str, spaces: int = 4) -> str:
    """
    Convert spaces to tabs in content.
    
    Converts leading spaces at the beginning of lines to tabs,
    where sequences of N spaces are converted to tabs, and any remaining
    spaces are left as spaces for position adjustment.
    
    Args:
        content: The content to convert
        spaces: Number of spaces to treat as one tab (default: 4)
    
    Returns:
        Content with leading spaces converted to tabs, preserving remaining spaces
    """
    lines = content.split('\n')
    converted_lines = []
    
    for line in lines:
        # Count leading spaces
        leading_spaces = len(line) - len(line.lstrip(' '))
        
        if leading_spaces > 0:
            # Convert leading spaces to tabs and remaining spaces
            num_tabs = leading_spaces // spaces
            remaining_spaces = leading_spaces % spaces
            rest_of_line = line[leading_spaces:]
            converted_line = '\t' * num_tabs + ' ' * remaining_spaces + rest_of_line
            converted_lines.append(converted_line)
        else:
            converted_lines.append(line)
    
    return '\n'.join(converted_lines)
