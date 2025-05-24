# pratilogin_main.py
import os
import sys
import logging
import time # For main loop delays, etc.

# --- Setup Colorama (should be among the first imports) ---
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    SUCCESS_COLOR = Fore.GREEN
    ERROR_COLOR = Fore.RED
    WARNING_COLOR = Fore.YELLOW
    RESET_COLOR = Style.RESET_ALL # Though autoreset=True handles most Fore resets
    INFO_COLOR = Fore.CYAN
except ImportError:
    print("Colorama library not found. Colors will not be available.")
    print("Please install it: pip install colorama")
    # Define dummy color variables if colorama is not available
    SUCCESS_COLOR = ERROR_COLOR = WARNING_COLOR = RESET_COLOR = INFO_COLOR = ""

# --- Import constants early ---
# This needs to happen after colorama setup if constants use colors,
# but before other modules that might depend on constants.
try:
    from constants import (
        APP_DIR, 
        EXE_PATH, 
        CONFIG_FILE, 
        LOG_FILE,
        DEFAULT_USERNAME_PLACEHOLDER, 
        KEYRING_SERVICE_NAME,

        # Network status Constants
        LOGIN_SUCCESSFUL, 
        REACHABLE_AUTH_FAILED_401, 
        REACHABLE_AUTH_OK_NO_INTERNET,
        REACHABLE_POST_ERROR, 
        NO_LOCATION_REACHABLE, 
        ALREADY_CONNECTED, 
        MISSING_CREDENTIALS,

        # fORCE RECONNECTION CONSTANTS
        MAX_FORCE_RETRIES,
        FORCE_RETRY_DELAY
    )
except ImportError:
    print(f"{ERROR_COLOR}FATAL: constants.py not found. Exiting.{RESET_COLOR}")
    sys.exit(1)

# --- System Operations (needs to be early for move_executable) ---
try:
    import system_ops
except ImportError:
    print(f"{ERROR_COLOR}FATAL: system_ops.py not found. Exiting.{RESET_COLOR}")
    sys.exit(1)

# --- Initial system setup: Ensure app directory and attempt self-move if needed ---
# This should happen before logging is fully configured to APP_DIR if it doesn't exist
system_ops.ensure_app_dir_exists()
if system_ops.is_windows() and hasattr(sys, 'frozen'): # Only for compiled Windows apps
    if not system_ops.is_running_from_appdata():
        print(f"{INFO_COLOR}Prima esecuzione o eseguibile in posizione non standard.{RESET_COLOR}")
        system_ops.move_executable_and_restart() # This will exit if it moves and restarts

# --- Setup Logging ---
def setup_logging():
    log_level = logging.INFO # Or logging.DEBUG for more verbosity
    # Make sure APP_DIR exists before setting up log file there
    system_ops.ensure_app_dir_exists()
    logging.basicConfig(
        filename=LOG_FILE,
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Also log to console for immediate feedback (can be higher level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING) # Log warnings and above to console
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    # logging.getLogger().addHandler(console_handler) # Uncomment to add console logging for library logs

setup_logging()
logging.info("PratiLogin application started.")
logging.info(f"Running from: {system_ops.get_current_executable_path()}")
logging.info(f"AppData directory: {APP_DIR}")


# --- Import other custom modules (now that logging and paths are set) ---
try:
    import config_manager
    import credential_manager
    import network_ops
except ImportError as e:
    logging.critical(f"Failed to import a core module: {e}. Ensure all .py files are present.")
    print(f"{ERROR_COLOR}FATAL: Manca un file del programma ({e.name}.py). Uscita.{RESET_COLOR}")
    sys.exit(1)


def print_title():
    print(f"{INFO_COLOR}╔══════════════════════════════════════════════════════╗{RESET_COLOR}")
    print(f"{INFO_COLOR}║            {SUCCESS_COLOR}Fast PratiLogin {VERSION if 'VERSION' in globals() else 'v?.?'}            {INFO_COLOR}║{RESET_COLOR}")
    print(f"{INFO_COLOR}╚══════════════════════════════════════════════════════╝{RESET_COLOR}")
    print(f"Configurazione in: {APP_DIR}")

def print_help():
    print(f"\n{INFO_COLOR}===== AIUTO PratiLogin ====={RESET_COLOR}")
    print(f"{SUCCESS_COLOR}r / invio{RESET_COLOR}: Tenta la connessione / Verifica stato connessione")
    print(f"{SUCCESS_COLOR}f{RESET_COLOR}:          Forza un nuovo tentativo di login")
    print(f"{SUCCESS_COLOR}l{RESET_COLOR}:          Cambia le credenziali UNIPI salvate")
    print(f"{SUCCESS_COLOR}o{RESET_COLOR}:          Apri la cartella dei file dell'applicazione")
    print(f"{SUCCESS_COLOR}d{RESET_COLOR}:          Disinstalla PratiLogin")
    print(f"{SUCCESS_COLOR}h{RESET_COLOR}:          Mostra questo aiuto")
    print(f"{SUCCESS_COLOR}c / q{RESET_COLOR}:      Chiudi il programma")
    print(f"{INFO_COLOR}============================{RESET_COLOR}\n")

VERSION = "1.0.0-keyring" # Simple versioning

def handle_credential_setup(config):
    """Handles initial credential setup or loading."""
    username = config_manager.get_username_from_config(config)
    password = None

    if username == DEFAULT_USERNAME_PLACEHOLDER:
        print(f"\n{WARNING_COLOR}Primo avvio o username non configurato.{RESET_COLOR}")
        print("È necessario inserire le credenziali UNIPI.")
        new_username, new_password = credential_manager.prompt_for_credentials()
        if new_username and new_password:
            if credential_manager.save_credentials(new_username, new_password):
                username = new_username
                password = new_password
                config_manager.store_username_in_config(config, username)
                config_manager.mark_first_run_completed(config) # Mark setup as done
                print(f"{SUCCESS_COLOR}Credenziali salvate per {username} nel portachiavi di sistema.{RESET_COLOR}")
            else:
                print(f"{ERROR_COLOR}Impossibile salvare le credenziali. Controlla i log.{RESET_COLOR}")
                # No usable credentials, might need to exit or retry
                return None, None # Indicate failure
        else:
            print(f"{ERROR_COLOR}Setup credenziali annullato o fallito.{RESET_COLOR}")
            return None, None # Indicate failure
    else:
        # Username exists, try to load password
        password = credential_manager.load_password(username)
        if not password:
            print(f"\n{WARNING_COLOR}Password per l'utente '{username}' non trovata nel portachiavi.{RESET_COLOR}")
            print(f"Potrebbe essere stata rimossa o il portachiavi non è accessibile.")
            print(f"Reinserisci la password per {username}:")
            _, new_password = credential_manager.prompt_for_credentials(
                prompt_username=f"Username (attuale: {username}, premi invio per confermare): ",
                prompt_password=f"Password per {username}: "
            ) # Username prompt is just for show, we use existing `username`
            if new_password:
                if credential_manager.save_credentials(username, new_password):
                    password = new_password
                    print(f"{SUCCESS_COLOR}Password aggiornata per {username} nel portachiavi.{RESET_COLOR}")
                else:
                    print(f"{ERROR_COLOR}Impossibile salvare la nuova password.{RESET_COLOR}")
                    return username, None # Username known, password failed to save
            else:
                print(f"{ERROR_COLOR}Aggiornamento password annullato.{RESET_COLOR}")
                return username, None # Username known, password not provided

    return username, password


def main():
    print_title()
    logging.info("Main function started.")

    config, is_first_run_logic = config_manager.load_config()
    logging.info(f"Config loaded. Is first run (logic based): {is_first_run_logic}")

    username, password = handle_credential_setup(config)

    if not username or not password or username == DEFAULT_USERNAME_PLACEHOLDER:
        print(f"\n{ERROR_COLOR}Credenziali non disponibili o setup incompleto. Impossibile procedere.{RESET_COLOR}")
        logging.critical("Credentials not available after setup attempt. Exiting.")
        input("Premi invio per uscire.")
        sys.exit(1)

    locations_map = config_manager.get_locations(config)
    if not locations_map:
        print(f"{ERROR_COLOR}Nessuna location definita nel file di configurazione. Impossibile procedere.{RESET_COLOR}")
        logging.critical("No locations found in config. Exiting.")
        input("Premi invio per uscire.")
        sys.exit(1)
    
    # Order locations: try last connected one first
    ordered_locations = {}
    last_loc = config_manager.get_last_location(config)
    if last_loc and last_loc in locations_map:
        ordered_locations[last_loc] = locations_map[last_loc]
    for loc, url in locations_map.items():
        if loc != last_loc:
            ordered_locations[loc] = url
    
    if is_first_run_logic:
        print(f"\n{INFO_COLOR}Primo avvio: Tento la connessione automaticamente...{RESET_COLOR}")
        status, loc_name = network_ops.try_login(
            ordered_locations, username, password,
            SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR, RESET_COLOR, force=True
        )
        if loc_name: # If a location was attempted (even if failed post)
            config_manager.update_last_location(config, loc_name)
        if status == LOGIN_SUCCESSFUL:
            print(f"{SUCCESS_COLOR}Connesso a {loc_name} e salvato come ultima location.{RESET_COLOR}")
        # Other statuses already print messages within try_login

    skip_next_auto_login = False

    while True:
        if not skip_next_auto_login:
            print(f"\n{INFO_COLOR}Verifica connessione / Tentativo di login... (Premi 'h' per aiuto){RESET_COLOR}")
            
            current_last_loc_name = config_manager.get_last_location(config)
            loc_to_try_first = None
            # Build current_ordered_locations with current_last_loc_name first
            current_ordered_locations = {}
            if current_last_loc_name and current_last_loc_name in locations_map:
                loc_to_try_first = current_last_loc_name
                current_ordered_locations[current_last_loc_name] = locations_map[current_last_loc_name]
            for l_key, l_url in locations_map.items():
                if l_key != current_last_loc_name:
                    current_ordered_locations[l_key] = l_url
            
            # Normal attempt - tries ordered_locations, specific_location_to_try is None initially
            status, loc_name = network_ops.try_login(
                current_ordered_locations, username, password,
                SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR, RESET_COLOR, force=False
            )

            if loc_name: # A location was at least targeted and GET attempted
                config_manager.update_last_location(config, loc_name)
            
            if status == LOGIN_SUCCESSFUL:
                pass # Message already printed
            elif status == ALREADY_CONNECTED:
                pass # Message already printed
            elif status == REACHABLE_AUTH_FAILED_401:
                # Message in try_login is quite descriptive.
                # Main loop doesn't need to do much more here for a normal attempt.
                pass
            elif status == NO_LOCATION_REACHABLE:
                print(f"{ERROR_COLOR}Nessun blocco del campus sembra raggiungibile al momento.{RESET_COLOR}")
            # Other statuses have messages in try_login

        skip_next_auto_login = False

        print(f"\n{INFO_COLOR}Azioni: [R]iprova/Stato, [F]orza login, [L]ogin cambia, [O]pen folder, [D]isinstalla, [H]elp, [C]hiudi{RESET_COLOR}")
        user_input = input("Scegli un'opzione: ").lower().strip()

        if user_input in ['c', 'q', 'chiudi']:
            logging.info("User chose to exit.")
            break
        elif user_input in ['l', 'login']:
            print(f"\n{INFO_COLOR}--- Cambio Credenziali ---{RESET_COLOR}")
            old_username = config_manager.get_username_from_config(config)
            
            new_username_input, new_password_input = credential_manager.prompt_for_credentials()

            if new_username_input and new_password_input:
                # Delete old credentials if username changed or if it's good practice
                if old_username and old_username != DEFAULT_USERNAME_PLACEHOLDER and old_username != new_username_input:
                    credential_manager.delete_credentials(old_username) # Delete for old user
                
                if credential_manager.save_credentials(new_username_input, new_password_input):
                    username = new_username_input # Update active username
                    password = new_password_input # Update active password
                    config_manager.store_username_in_config(config, username)
                    print(f"{SUCCESS_COLOR}Credenziali aggiornate per {username}.{RESET_COLOR}")
                    logging.info(f"Credentials updated for user {username}.")
                    print("Riprovo la connessione con le nuove credenziali...")
                    skip_next_auto_login = False # Force a login attempt
                else:
                    print(f"{ERROR_COLOR}Salvataggio nuove credenziali fallito.{RESET_COLOR}")
                    logging.error("Failed to save new credentials during change.")
                    skip_next_auto_login = True # Don't try with potentially bad state
            else:
                print("Cambio credenziali annullato.")
                skip_next_auto_login = True

        # For 'f' (force login):
        elif user_input == 'f':
            print(f"\n{INFO_COLOR}--- Modalità Login Forzato ---{RESET_COLOR}") # Changed title for clarity
            force_location_target = config_manager.get_last_location(config)
            
            if not force_location_target or force_location_target not in locations_map:
                print(f"{INFO_COLOR}Nessuna ultima location valida, cerco una sede raggiungibile...{RESET_COLOR}")
                # When finding an initial target, iterate all locations
                status_find, found_loc = network_ops.try_login(
                    locations_map, username, password, 
                    SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR, RESET_COLOR, 
                    force=True, specific_location_to_try=None # Iterate all
                )
                if found_loc: 
                    config_manager.update_last_location(config, found_loc) # Save if found
                    force_location_target = found_loc # This is now our target
                # If status_find is NO_LOCATION_REACHABLE or found_loc is None, error printed below
            
            if not force_location_target: # Check again after trying to find one
                 print(f"{ERROR_COLOR}Impossibile determinare una sede per forzare il login.{RESET_COLOR}")
                 skip_next_auto_login = True
                 continue # Go back to main loop prompt

            print(f"{INFO_COLOR}Tenterò di forzare il login su '{force_location_target}' fino a {MAX_FORCE_RETRIES} volte.{RESET_COLOR}")
            retries = 0
            force_success = False
            while retries < MAX_FORCE_RETRIES:
                retries += 1
                print(f"{INFO_COLOR}Tentativo forzato {retries}/{MAX_FORCE_RETRIES} su '{force_location_target}'...{RESET_COLOR}")
                
                # In the force loop, ALWAYS try the specific force_location_target
                # The try_login function itself handles if this target becomes unreachable
                current_status, current_loc_name = network_ops.try_login( # <-- GET TUPLE HERE
                    locations_map, username, password, 
                    SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR, RESET_COLOR,
                    force=True, specific_location_to_try=force_location_target
                )

                # current_loc_name from try_login will be force_location_target if it was attempted,
                # or None if something went wrong before even trying (e.g. MISSING_CREDENTIALS)
                # or if specific_location_to_try was not in locations_map (shouldn't happen here)
                if current_loc_name: 
                    config_manager.update_last_location(config, current_loc_name)
                    # It's possible try_login iterated if specific_location_to_try was initially bad,
                    # so update force_location_target to what was actually last attempted.
                    force_location_target = current_loc_name 


                if current_status == LOGIN_SUCCESSFUL:
                    print(f"{SUCCESS_COLOR}Login forzato riuscito su '{current_loc_name}'!{RESET_COLOR}")
                    force_success = True
                    break
                elif current_status == NO_LOCATION_REACHABLE:
                    # This means the specific_location_to_try (force_location_target) became unreachable
                    print(f"{ERROR_COLOR}'{force_location_target}' non è più raggiungibile. Interrompo i tentativi forzati.{RESET_COLOR}")
                    break 
                elif current_status in [REACHABLE_AUTH_FAILED_401, REACHABLE_AUTH_OK_NO_INTERNET, REACHABLE_POST_ERROR]:
                    if retries < MAX_FORCE_RETRIES:
                        print(f"{WARNING_COLOR}Login su '{force_location_target}' non completato (stato: {current_status}). Riprovo tra {FORCE_RETRY_DELAY} sec...{RESET_COLOR}")
                        time.sleep(FORCE_RETRY_DELAY)
                    else:
                        print(f"{ERROR_COLOR}Numero massimo di tentativi forzati raggiunto per '{force_location_target}'. Login fallito.{RESET_COLOR}")
                elif current_status == ALREADY_CONNECTED: 
                    print(f"{SUCCESS_COLOR}Risulta già connesso durante il tentativo forzato.{RESET_COLOR}")
                    force_success = True
                    break
                else: # MISSING_CREDENTIALS or other unexpected
                    print(f"{ERROR_COLOR}Errore ({current_status}) durante il login forzato. Interrompo.{RESET_COLOR}")
                    break
            
            if not force_success:
                print(f"{ERROR_COLOR}Modalità login forzato terminata senza successo.{RESET_COLOR}")
            skip_next_auto_login = True

        elif user_input in ['r', 'riprova', '']: # Enter also retries
            skip_next_auto_login = False # Will trigger the auto-login attempt at loop start

        elif user_input == 'h':
            print_help()
            skip_next_auto_login = True

        elif user_input == 'o':
            system_ops.open_app_data_folder()
            skip_next_auto_login = True

        elif user_input == 'd':
            print(f"\n{WARNING_COLOR}ATTENZIONE: Stai per disinstallare PratiLogin.{RESET_COLOR}")
            confirm = input("Sei sicuro? (s/N): ").lower()
            if confirm == 's':
                username_for_uninstall = config_manager.get_username_from_config(config)
                system_ops.uninstall_application(
                    username_for_uninstall,
                    credential_manager.delete_credentials
                )
                # uninstall_application calls sys.exit()
            else:
                print("Disinstallazione annullata.")
                skip_next_auto_login = True
        else:
            print(f"{WARNING_COLOR}Comando non riconosciuto. Premi 'h' per aiuto.{RESET_COLOR}")
            skip_next_auto_login = True
        
        time.sleep(0.1) # Small delay

    print(f"\n{INFO_COLOR}PratiLogin terminato. Arrivederci!{RESET_COLOR}")
    logging.info("Application shutdown gracefully.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{WARNING_COLOR}Uscita interrotta dall'utente.{RESET_COLOR}")
        logging.warning("Application terminated by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"{ERROR_COLOR}Si è verificato un errore imprevisto: {e}{RESET_COLOR}")
        logging.critical(f"Unhandled exception in main: {e}", exc_info=True)
    finally:
        logging.info("PratiLogin final shutdown sequence.")
        sys.exit(0)