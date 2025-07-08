import sys
import configparser
import importlib
import json
import os
from typing import List, Dict, Tuple, Optional

# Global dictionary to hold translation strings.
MESSAGES: Dict[str, str] = {}

def load_config(path: str = 'config.ini') -> configparser.ConfigParser:
    """
    Reads and returns the content of the configuration file.

    Args:
        path (str): The path to the configuration file.

    Returns:
        configparser.ConfigParser: The parsed configuration.
    """
    config = configparser.ConfigParser()
    if not os.path.exists(path):
        # This error is hardcoded in English as translations are not yet loaded.
        print(f"Error: Configuration file '{path}' not found.")
        sys.exit(1)
    try:
        config.read(path, encoding='utf-8')
        return config
    except configparser.Error as e:
        # This error is also hardcoded.
        print(f"Error reading the configuration file: {e}")
        sys.exit(1)

def load_translations(config: configparser.ConfigParser):
    """
    Loads translation strings from a JSON file into the global MESSAGES dictionary.
    It always loads English as a fallback, then overwrites with the selected language.
    """
    global MESSAGES
    lang_code = config.get('settings', 'language', fallback='en')
    base_path = 'lang'
    fallback_lang_path = os.path.join(base_path, 'en.json')
    
    try:
        with open(fallback_lang_path, 'r', encoding='utf-8') as f:
            MESSAGES = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Use a hardcoded message if the essential English language file is missing.
        print(f"Critical Error: Fallback language file '{fallback_lang_path}' not found or is invalid.")
        sys.exit(1)

    if lang_code != 'en':
        target_lang_path = os.path.join(base_path, f'{lang_code}.json')
        try:
            with open(target_lang_path, 'r', encoding='utf-8') as f:
                specific_translations = json.load(f)
            MESSAGES.update(specific_translations)
        except (FileNotFoundError, json.JSONDecodeError):
            # If the target language file is missing, the English fallback will be used.
            pass

def display_help(config: configparser.ConfigParser):
    """
    Displays the usage guide and available commands/aliases.
    """
    print(MESSAGES.get("usage", "Usage: main.py <command> [arguments]"))
    print("\n" + MESSAGES.get("available_commands", "Available commands:"))
    
    if 'commands' in config:
        for command in config['commands']:
            print(f"- {command}")
            
    if 'aliases' in config and config['aliases']:
        print("\n" + MESSAGES.get("available_aliases", "Aliases:"))
        for alias, command in config['aliases'].items():
            print(f"- {alias} -> {command}")

def resolve_command(
    config: configparser.ConfigParser, 
    cli_args: List[str]
) -> Optional[Tuple[str, List[str]]]:
    """
    Resolves an alias (if used) for the command and its parameters,
    and returns the actual command and its final arguments.

    Args:
        config: The parsed configuration.
        cli_args: The command-line arguments.

    Returns:
        A tuple of (command, arguments), or None if the command is invalid.
    """
    command, *user_args = cli_args
    aliases = config['aliases'] if 'aliases' in config else {}

    # Resolve alias for the main command
    if command in aliases:
        alias_definition = aliases[command].split()
        command = alias_definition[0]
        args = alias_definition[1:] + user_args
    else:
        args = user_args
    
    # Resolve aliases for parameters
    resolved_args = []
    for arg in args:
        if arg in aliases:
            resolved_args.extend(aliases[arg].split())
        else:
            resolved_args.append(arg)

    # Check if the final command is valid
    if 'commands' not in config or command not in config['commands']:
        return None
        
    return command, resolved_args

def execute_command(config: configparser.ConfigParser, command: str, args: List[str]):
    """
    Dynamically loads and runs the module associated with the command.
    It also expands user and environment variables in the arguments.
    """
    # Expand OS-specific path variables like '~' or '$HOME'
    expanded_args = [os.path.expandvars(os.path.expanduser(arg)) for arg in args]

    try:
        module_name = config['commands'][command]
        module_to_run = importlib.import_module(module_name)
        
        if hasattr(module_to_run, 'run') and callable(getattr(module_to_run, 'run')):
            module_to_run.run(expanded_args)
        else:
            print(MESSAGES.get("module_missing_run_function", "Module '{0}' has no 'run' function.").format(module_name))
            sys.exit(1)
            
    except ImportError:
        print(MESSAGES.get("import_error", "Failed to import module '{0}'.").format(module_name))
        sys.exit(1)
    except Exception as e:
        print(MESSAGES.get("module_run_error", "Error running module: {0}").format(e))
        sys.exit(1)

def main():
    """The main entry point for the application."""
    config = load_config()
    load_translations(config)

    if len(sys.argv) < 2:
        display_help(config)
        sys.exit(0)

    resolved = resolve_command(config, sys.argv[1:])
    
    if resolved is None:
        original_command = sys.argv[1]
        print(MESSAGES.get("unknown_command", "Unknown command: {0}").format(original_command))
        display_help(config)
        sys.exit(1)
        
    command, args = resolved
    execute_command(config, command, args)

if __name__ == "__main__":
    main()
