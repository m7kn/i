import os
import glob


def is_pattern(text):
      return '*' in text or '?' in text or '[' in text


def run(args=None):
    """
    Lists files and directories based on a path or a pattern.

    By default, it prints the contents to the console.

    Args:
        args (list, optional): A list of string arguments. Possible values:
            - A path or pattern (e.g., './folder', '*.txt', 'src/*.py').
              If no path is provided, it defaults to the current directory ('.').
            - 'sort' or 'asc': Sorts the output in ascending order.
            - 'desc': Sorts the output in descending order.
            - 'list': The function will return the result as a Python list
                      instead of printing it to the console.
    """
    if args is None:
        args = []

    # Set default values
    path_or_pattern = '.'
    sort_order = None  # 'asc', 'desc', or None
    return_as_list = False

    # Parse arguments
    keywords = {'sort', 'asc', 'desc', 'list'}
    for arg in args:
        if arg in ('sort', 'asc'):
            sort_order = 'asc'
        elif arg == 'desc':
            sort_order = 'desc'
        elif arg == 'list':
            return_as_list = True
        elif arg not in keywords:
            # Assume any argument that is not a keyword is the path or pattern
            path_or_pattern = arg

    # Get the list of contents using either glob or scandir
    content = []
    # Check if the input string is a pattern (contains wildcards)
    if is_pattern(path_or_pattern):
        # Use glob to find all paths matching the pattern
        content = glob.glob(path_or_pattern)
        if not content:
            # It's not an error if a pattern finds no matches, so we just inform the user.
            print(f"No items found matching pattern: '{path_or_pattern}'")
            return
    else:
        # It's a regular directory path, use scandir
        if not os.path.isdir(path_or_pattern):
            print(f"Error: Path is not a valid directory: '{path_or_pattern}'")
            return
        try:
            # Use os.scandir for better performance as it fetches file type info
            with os.scandir(path_or_pattern) as entries:
                content = [entry.name for entry in entries]
        except FileNotFoundError:
            # This is a fallback, though isdir should prevent this.
            error_message = f"Error: Directory not found: '{path_or_pattern}'"
            if return_as_list:
                return [error_message]
            else:
                print(error_message)
                return

    # Sort the contents if requested
    if sort_order:
        content.sort(reverse=sort_order=='desc')

    # Print to console
    if not return_as_list:
        print(content)
    else:
        for item in content:
            print(item)
