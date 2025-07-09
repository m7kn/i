from cpuinfo import get_cpu_info, get_cpu_info_json
import textwrap
import shutil
import json


def run(args=None):
    # keywords = {'sort', 'asc', 'desc', 'array', 'dict', 'list', 'json', 'border'}
    sort_order = None  # 'asc', 'desc', or None
    return_as = "dict" # 'array', 'dict', 'list', 'table' or 'json'
    border = False
    if args and "json" in args:
        return_as = "json"
        data = json.loads(get_cpu_info_json())
    else:
        data = get_cpu_info() 
    for arg in args:
        if arg in ('sort', 'asc'):
            sort_order = 'asc'
        elif arg == 'desc':
            sort_order = 'desc'
        elif arg == "array":
            return_as = "array"
        elif arg == 'list':
            return_as = "list"
        elif arg == 'table':
            return_as = "table"
        elif arg == 'border':
            border = True

    results = data

    try:
        del results['python_version']
        del results['cpuinfo_version']
        del results['cpuinfo_version_string']
    except:
        pass

    if sort_order:
        results = dict(sorted(data.items(), reverse=sort_order=='desc'))

    if return_as == "list":
        for key, value in results.items():
            print("{0}: {1}".format(key, value))
    elif return_as == "array":
        print(list(results.items()))
    elif return_as == "dict" or return_as == "json":
        print(results)
    elif return_as == "table":
        if not border:
            left_column_width = max(len(key) for key in results.keys()) + 1            
            for key, value in results.items():
                print(f"{key:<{left_column_width}}{value}")
        else:
            try:
                # Get the current width of the terminal
                terminal_width = shutil.get_terminal_size().columns
            except OSError:
                # Provide a fallback width if not running in a real terminal (e.g., in some IDEs)
                terminal_width = 80

            # Column width calculation
            key_col_width = max(len(key) for key in results.keys())
            
            # Calculate the total width used by table borders and padding
            # Format: │<space>KEY<space>│<space>VALUE<space>│  (7 characters total)
            empty_width = 7

            # Calculate the remaining space for the value column
            value_col_width = terminal_width - key_col_width - empty_width

            # Ensure the value column has a minimum reasonable width to avoid errors
            if value_col_width < 10:
                print("Terminal is too narrow to display the table properly.")
                exit() 

            # Top border
            print(f"┌{'─' * (key_col_width + 2)}┬{'─' * (value_col_width + 2)}┐")

            # Iterate through items with an index for drawing separators
            num_items = len(results)
            for i, (key, value) in enumerate(results.items()):
                value_str = str(value)
                
                # Wrap the value text into a list of lines
                wrapped_value_lines = textwrap.wrap(value_str, width=value_col_width)
                
                # Ensure there's at least one line, even for empty values
                if not wrapped_value_lines:
                    wrapped_value_lines.append("")

                # Print the first line, which contains the key
                print(f"│ {key:<{key_col_width}} │ {wrapped_value_lines[0]:<{value_col_width}} │")
                
                # Print subsequent lines of a wrapped value, with an empty key column
                for line in wrapped_value_lines[1:]:
                    print(f"│ {' ':<{key_col_width}} │ {line:<{value_col_width}} │")

                # Print a separator line, but not after the last item
                if i < num_items - 1:
                    print(f"├{'─' * (key_col_width + 2)}┼{'─' * (value_col_width + 2)}┤")

            # Bottom border
            print(f"└{'─' * (key_col_width + 2)}┴{'─' * (value_col_width + 2)}┘")
