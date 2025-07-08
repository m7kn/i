import os

def run(args=None):
    """
    Lists the contents of a directory based on the provided arguments.

    By default, it prints the contents to the console.

    Args:
        args (list, optional): A list of string arguments. Possible values:
            - A path to a directory (e.g., './folder' or 'C:/Users').
              If no path is provided, it defaults to the current directory.
            - 'sort' or 'asc': Sorts the output in ascending order.
            - 'desc': Sorts the output in descending order.
            - 'list': The function will return the result as a Python list
                      instead of printing it to the console.
    """
    if args is None:
        args = []

    # --- Step 1: Set default values ---
    path = '.'
    sort_order = None  # 'asc', 'desc', or None
    return_as_list = False

    # --- Step 2: Parse arguments ---
    keywords = {'sort', 'asc', 'desc', 'list'}
    for arg in args:
        if arg in ('sort', 'asc'):
            sort_order = 'asc'
        elif arg == 'desc':
            sort_order = 'desc'
        elif arg == 'list':
            return_as_list = True
        elif arg not in keywords:
            # Assume any argument that is not a keyword is the path
            path = arg

    # --- Step 3: Validate the path ---
    if not os.path.isdir(path):
        print(f"Error: The specified path does not exist or is not a directory: '{path}'")
        return

    # --- Step 4: Read directory contents ---
    try:
        # Use os.scandir for better performance as it fetches file type info
        with os.scandir(path) as entries:
            content = [entry.name for entry in entries]
    except FileNotFoundError:
        # This is a fallback, though isdir should prevent this.
        error_message = f"Error: Directory not found: '{path}'"
        if return_as_list:
            return [error_message]
        else:
            print(error_message)
            return

    # --- Step 5: Sort the contents if requested ---
    if sort_order == 'asc':
        content.sort()
    elif sort_order == 'desc':
        content.sort(reverse=True)

    # --- Step 6: Print to console ---
    if not return_as_list:
        print(content)
    else:
        for item in content:
            print(item)
