# system_ops.py
import os
import shutil
import sys
import subprocess
import platform
import logging
import time # For uninstall pause

from constants import APP_DIR, EXE_PATH, CONFIG_FILE, LOG_FILE, EXE_NAME

# Conditional import for Windows specific features
if platform.system() == "Windows":
    import winshell
    from win32com.client import Dispatch
else:
    winshell = None
    Dispatch = None

def is_windows() -> bool:
    """Checks if the current OS is Windows."""
    return platform.system() == "Windows"

def get_current_executable_path() -> str:
    """Gets the path of the currently running executable or script."""
    if getattr(sys, 'frozen', False):  # Bundled app (PyInstaller)
        return sys.executable
    return os.path.abspath(sys.argv[0])

def is_running_from_appdata() -> bool:
    """Checks if the script is running from the designated APP_DIR."""
    current_path = get_current_executable_path()
    # On Windows, EXE_PATH is where it *should* be.
    # For other OS, if this script is not an "exe", current_path will be the .py file.
    # This check is primarily for the Windows .exe self-location behavior.
    if is_windows():
        return current_path.lower() == EXE_PATH.lower()
    # For non-Windows or non-frozen scripts, this check might need adjustment
    # or might not be relevant if self-moving isn't implemented.
    # For now, assume it's "correct" if not on Windows or not the target EXE_PATH.
    return True # Or implement specific logic for other OS if needed


def ensure_app_dir_exists():
    """Ensures the application directory in AppData exists."""
    if not os.path.exists(APP_DIR):
        try:
            os.makedirs(APP_DIR)
            logging.info(f"Application directory created: {APP_DIR}")
        except OSError as e:
            logging.error(f"Error creating application directory {APP_DIR}: {e}")
            # Depending on severity, might want to exit or raise
            print(f"ERRORE CRITICO: Impossibile creare la cartella dell'applicazione: {APP_DIR}")
            sys.exit(1)


def create_shortcut_on_desktop(target_path: str, app_dir_for_working_dir: str):
    """Creates a shortcut on the desktop (Windows only)."""
    if not is_windows() or not winshell or not Dispatch:
        logging.warning("Shortcut creation is only supported on Windows.")
        return

    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, f"{os.path.splitext(EXE_NAME)[0]}.lnk")

    try:
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = app_dir_for_working_dir # Set working dir to AppData
        shortcut.IconLocation = target_path # Optional: use icon from exe
        shortcut.Description = "Accesso rapido a PratiLogin"
        shortcut.save()
        logging.info(f"Desktop shortcut created: {shortcut_path}")
        print(f"Collegamento creato sul desktop: {shortcut_path}")
    except Exception as e:
        logging.error(f"Error creating desktop shortcut: {e}")
        print(f"Errore durante la creazione del collegamento: {e}")


def move_executable_and_restart():
    """Moves the executable to APP_DIR and restarts (Windows .exe context primarily)."""
    if not is_windows(): # This behavior is primarily for Windows .exe self-management
        logging.info("Move_executable_and_restart is a Windows-specific behavior, skipping.")
        return

    current_exe_path = get_current_executable_path()
    if current_exe_path.lower() == EXE_PATH.lower():
        logging.info("Executable already in the correct AppData location.")
        return

    ensure_app_dir_exists() # Ensure APP_DIR exists before copying

    try:
        logging.info(f"Attempting to copy executable from {current_exe_path} to {EXE_PATH}")
        shutil.copy(current_exe_path, EXE_PATH)
        logging.info(f"Executable copied to {EXE_PATH}")

        create_shortcut_on_desktop(EXE_PATH, APP_DIR)

        print(f"\nL'applicazione è stata spostata in {EXE_PATH}")
        print(f"Riavvio da {APP_DIR}...")

        subprocess.Popen([EXE_PATH])
        sys.exit(0) # Exit current instance
    except Exception as e:
        logging.error(f"Error during move_executable_and_restart: {e}")
        print(f"Errore durante lo spostamento e il riavvio: {e}")
        # Potentially offer to run from current location or exit
        # input("Premi Invio per tentare di continuare dall'attuale posizione...")


def uninstall_application(username_to_delete_creds: str | None, delete_creds_func):
    """Uninstalls the application."""
    print("\nDisinstallazione in corso...")
    logging.info("Uninstall process started.")

    # 1. Attempt to delete credentials from keyring
    if username_to_delete_creds and username_to_delete_creds != "username_not_set": # from constants
        if delete_creds_func(username_to_delete_creds):
            print("Credenziali utente rimosse dal portachiavi di sistema.")
            logging.info(f"Credentials for {username_to_delete_creds} removed from keyring.")
        else:
            print("Attenzione: Impossibile rimuovere le credenziali dal portachiavi (potrebbero non esistere più o errore).")
            logging.warning(f"Could not remove credentials for {username_to_delete_creds} from keyring during uninstall.")
    else:
        print("Nessun username configurato, salto la rimozione credenziali dal portachiavi.")
        logging.info("No username found in config, skipping credential deletion from keyring.")

    # 2. Remove desktop shortcut (Windows)
    if is_windows() and winshell:
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, f"{os.path.splitext(EXE_NAME)[0]}.lnk")
        if os.path.exists(shortcut_path):
            try:
                os.remove(shortcut_path)
                print("Collegamento sul desktop rimosso.")
                logging.info(f"Desktop shortcut removed: {shortcut_path}")
            except Exception as e:
                print(f"Errore durante la rimozione del collegamento: {e}")
                logging.error(f"Error removing shortcut {shortcut_path}: {e}")

    # 3. Remove files and directory
    files_to_remove = [CONFIG_FILE, LOG_FILE, EXE_PATH]
    for f_path in files_to_remove:
        if os.path.exists(f_path):
            try:
                os.remove(f_path)
                logging.info(f"File removed: {f_path}")
            except Exception as e:
                logging.error(f"Error removing file {f_path}: {e}")
                # Continue uninstall even if a file can't be removed

    if os.path.exists(APP_DIR):
        try:
            shutil.rmtree(APP_DIR) # This should remove EXE_PATH if it's inside and wasn't removed above
            print(f"Cartella dell'applicazione rimossa: {APP_DIR}")
            logging.info(f"Application directory removed: {APP_DIR}")
        except Exception as e:
            print(f"Errore durante la rimozione della cartella {APP_DIR}: {e}")
            logging.error(f"Error removing directory {APP_DIR}: {e}")
            print("Potrebbe essere necessario rimuovere manualmente la cartella.")

    print("\nPratiLogin è stato disinstallato.")
    logging.info("Uninstall process completed.")
    time.sleep(3)
    sys.exit(0)


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