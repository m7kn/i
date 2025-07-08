import sys
import configparser
import importlib
import json
import os

def load_translations(lang_code='en'):
    """
    Loads translation strings from a JSON file.
    It always loads English as a fallback, then overwrites with the selected language.
    If the specified language file is not found, it defaults to English without an error.
    """
    base_path = 'lang'
    fallback_lang_path = os.path.join(base_path, 'en.json')
    
    # --- 1. Load fallback language (English) ---
    try:
        with open(fallback_lang_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If English is missing, the program cannot function correctly.
        print(f"Critical Error: Fallback language file '{fallback_lang_path}' not found or is invalid.")
        sys.exit(1)

    # --- 2. If the selected language is not the fallback, try to load it ---
    if lang_code != 'en':
        target_lang_path = os.path.join(base_path, f'{lang_code}.json')
        try:
            with open(target_lang_path, 'r', encoding='utf-8') as f:
                specific_translations = json.load(f)
            # Update the base (English) translations with the specific language's strings
            translations.update(specific_translations)
        except (FileNotFoundError, json.JSONDecodeError):
            # If the target language file is missing or corrupt, just use the English fallback.
            # No error message is printed, as per the requirement.
            pass
            
    return translations

def main():
    """
    Main entry point for the program.
    It reads the configuration and the command-line argument,
    then executes the corresponding module.
    """
    # --- 1. Read configuration file ---
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
    except configparser.Error as e:
        # This initial error cannot be translated as we haven't loaded the language yet.
        print(f"Error reading the configuration file: {e}")
        sys.exit(1)

    # --- 2. Load language based on config ---
    # Defaults to 'en' if the setting is missing.
    lang_code = config.get('settings', 'language', fallback='en')
    MESSAGES = load_translations(lang_code)

    if 'commands' not in config:
        print(MESSAGES["config_section_missing"])
        sys.exit(1)

    # --- 3. Check command-line arguments ---
    if len(sys.argv) < 2:
        print(MESSAGES["usage"])
        print(MESSAGES["available_commands"])
        for command in config['commands']:
            print(f"- {command}")
        sys.exit(1)

    command = sys.argv[1]

    # --- 4. Find command in configuration ---
    if command not in config['commands']:
        print(MESSAGES["unknown_command"].format(command))
        print(MESSAGES["available_commands"])
        for cmd in config['commands']:
            print(f"- {cmd}")
        sys.exit(1)

    module_name = config['commands'][command]

    # --- 5. Dynamically load and run the module ---
    try:
        module_to_run = importlib.import_module(module_name)
        if hasattr(module_to_run, 'run') and callable(getattr(module_to_run, 'run')):
            # Get any additional arguments from the command line (after the command itself)
            args = sys.argv[2:]
            # Execute the module's 'run' function with the arguments
            module_to_run.run(args)
        else:
            print(MESSAGES["module_missing_run_function"].format(module_name))
            sys.exit(1)
    except ImportError:
        print(MESSAGES["import_error"].format(module_name))
        sys.exit(1)
    except Exception as e:
        print(MESSAGES["module_run_error"].format(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
