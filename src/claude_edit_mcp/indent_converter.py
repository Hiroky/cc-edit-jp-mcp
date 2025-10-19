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
    
    Converts sequences of N spaces at the beginning of lines to tabs,
    where N is the spaces parameter (default: 4).
    
    Args:
        content: The content to convert
        spaces: Number of spaces to treat as one tab (default: 4)
    
    Returns:
        Content with spaces converted to tabs
    """
    lines = content.split('\n')
    converted_lines = []
    space_str = ' ' * spaces
    
    for line in lines:
        # Count leading spaces in multiples of spaces parameter
        leading_spaces = len(line) - len(line.lstrip(' '))
        
        if leading_spaces > 0 and leading_spaces % spaces == 0:
            # Replace leading spaces with tabs
            num_tabs = leading_spaces // spaces
            rest_of_line = line[leading_spaces:]
            converted_line = '\t' * num_tabs + rest_of_line
            converted_lines.append(converted_line)
        else:
            converted_lines.append(line)
    
    return '\n'.join(converted_lines)
