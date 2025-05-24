# credential_manager.py
import keyring
import getpass
import logging
from constants import KEYRING_SERVICE_NAME, DEFAULT_USERNAME_PLACEHOLDER

def save_credentials(username: str, password: str) -> bool:
    """Saves credentials to the OS keyring."""
    try:
        keyring.set_password(KEYRING_SERVICE_NAME, username, password)
        logging.info(f"Credentials saved for user: {username}")
        return True
    except keyring.errors.NoKeyringError:
        logging.error("No keyring backend found. Cannot save credentials securely.")
        print(f"\n{Fore.RED}ERRORE: Nessun backend keyring trovato. Impossibile salvare le credenziali in modo sicuro.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Considera di installare un backend come 'keyrings.alt'.{Style.RESET_ALL}")
        return False
    except Exception as e:
        logging.error(f"Failed to save credentials for {username}: {e}")
        return False

def load_password(username: str) -> str | None:
    """Loads password from the OS keyring for the given username."""
    if not username or username == DEFAULT_USERNAME_PLACEHOLDER:
        logging.warning("Attempted to load password for an invalid/unset username.")
        return None
    try:
        password = keyring.get_password(KEYRING_SERVICE_NAME, username)
        if password:
            logging.info(f"Password loaded for user: {username}")
        else:
            logging.warning(f"No password found in keyring for user: {username}")
        return password
    except keyring.errors.NoKeyringError:
        logging.error("No keyring backend found. Cannot load credentials securely.")
        # This error should ideally be handled more globally or by prompting user
        return None
    except Exception as e:
        logging.error(f"Failed to load password for {username}: {e}")
        return None

def delete_credentials(username: str) -> bool:
    """Deletes credentials from the OS keyring."""
    if not username or username == DEFAULT_USERNAME_PLACEHOLDER:
        logging.warning("Attempted to delete credentials for an invalid/unset username.")
        return False
    try:
        keyring.delete_password(KEYRING_SERVICE_NAME, username)
        logging.info(f"Credentials deleted for user: {username}")
        return True
    except keyring.errors.PasswordDeleteError:
        logging.warning(f"Password for {username} not found in keyring or could not be deleted.")
        # This is not necessarily an error if we're just cleaning up
        return False
    except keyring.errors.NoKeyringError:
        logging.error("No keyring backend found. Cannot delete credentials.")
        return False
    except Exception as e:
        logging.error(f"Failed to delete credentials for {username}: {e}")
        return False

def prompt_for_credentials(prompt_username="Inserisci username UNIPI: ",
                           prompt_password="Inserisci password UNIPI: ") -> tuple[str | None, str | None]:
    """Prompts user for username and password."""
    new_username = input(prompt_username).strip()
    if not new_username:
        print("Username non può essere vuoto.")
        return None, None
    new_password = getpass.getpass(prompt_password)
    if not new_password:
        print("Password non può essere vuota.")
        return None, None
    return new_username, new_password

# For colorama in this module if used directly for prints
from colorama import Fore, Style # Keep at bottom to avoid circular if constants need colorama