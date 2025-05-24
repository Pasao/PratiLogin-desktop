import os
import sys
import subprocess
import platform
import logging
# import shutil # Non più necessario
# import time # Non più necessario

from constants import APP_DIR # Solo APP_DIR è necessario qui ora

# Conditional import for Windows specific features
# Non più necessarie perché le funzioni che le usavano sono state rimosse
# if platform.system() == "Windows":
#     import winshell
#     from win32com.client import Dispatch
# else:
#     winshell = None
#     Dispatch = None

def is_windows() -> bool:
    """Checks if the current OS is Windows."""
    return platform.system() == "Windows"

def get_current_executable_path() -> str:
    """Gets the path of the currently running executable or script."""
    if getattr(sys, 'frozen', False):  # Bundled app (PyInstaller)
        return sys.executable
    return os.path.abspath(sys.argv[0])

# def is_running_from_appdata() -> bool: # RIMOSSA
    # ...

def ensure_app_dir_exists():
    """Ensures the application directory in AppData exists."""
    if not os.path.exists(APP_DIR):
        try:
            os.makedirs(APP_DIR)
            logging.info(f"Application directory created: {APP_DIR}")
        except OSError as e:
            logging.error(f"Error creating application directory {APP_DIR}: {e}")
            print(f"ERRORE CRITICO: Impossibile creare la cartella dell'applicazione: {APP_DIR}")
            sys.exit(1)

# def create_shortcut_on_desktop(target_path: str, app_dir_for_working_dir: str): # RIMOSSA
    # ...

# def move_executable_and_restart(): # RIMOSSA
    # ...

# def uninstall_application(username_to_delete_creds: str | None, delete_creds_func): # RIMOSSA
    # ...

def open_app_data_folder():
    """Opens the application's data folder in the file explorer."""
    ensure_app_dir_exists() # Make sure it exists before trying to open
    try:
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{APP_DIR}"')
        elif platform.system() == "Darwin": # macOS
            subprocess.Popen(['open', APP_DIR])
        else: # Linux and other UNIX-like
            subprocess.Popen(['xdg-open', APP_DIR])
        print(f"\nCartella aperta: {APP_DIR}")
        logging.info(f"Opened app data folder: {APP_DIR}")
    except Exception as e:
        print(f"\nErrore durante l'apertura della cartella: {e}")
        logging.error(f"Error opening app data folder {APP_DIR}: {e}")