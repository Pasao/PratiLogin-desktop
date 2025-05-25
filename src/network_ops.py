# network_ops.py
import requests
import logging
import platform
import warnings
import time
from typing import Dict, Optional, Tuple

from constants import (
    NETWORK_CHECK_TIMEOUT, 
    LOGIN_SERVER_REACH_TIMEOUT, 
    LOGIN_AUTH_TIMEOUT, 
    LOGIN_SUCCESSFUL,
    REACHABLE_AUTH_FAILED_401, 
    REACHABLE_AUTH_OK_NO_INTERNET, 
    REACHABLE_POST_ERROR,
    NO_LOCATION_REACHABLE, 
    ALREADY_CONNECTED, 
    MISSING_CREDENTIALS
)


# Suppress InsecureRequestWarning for unverified HTTPS requests
warnings.simplefilter("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


def check_internet_connection() -> bool:
    """
    Checks for a working internet connection by hitting known 'generate_204' endpoints.
    Returns True if a connection seems active, False otherwise.
    """
    if platform.system() == 'Darwin': # macOS
        endpoints = [
            ("http://captive.apple.com/hotspot-detect.html", "apple"), # Primary for Mac
            ("http://clients3.google.com/generate_204", "google"),
        ]
    else: # Windows, Linux, etc.
        endpoints = [
            ("http://clients3.google.com/generate_204", "google"),
            ("http://www.msftconnecttest.com/connecttest.txt", "msft"),
        ]

    for url, label in endpoints:
        try:
            response = requests.get(url, timeout=NETWORK_CHECK_TIMEOUT, allow_redirects=False, verify=False)
            logging.info(f"Internet check ({label}): {url}, Status: {response.status_code}, Content Hint: {response.text[:30]}")

            if response.status_code == 204:
                logging.info("Connection verified (204 No Content).")
                return True
            if label == "apple" and "Success" in response.text: # Apple's specific success page
                 logging.info("Connection verified (Apple captive portal check success).")
                 return True
            if label == "msft" and "Microsoft Connect Test" in response.text:
                 logging.info("Connection verified (MSFT connect test success).")
                 return True
            # If a redirect occurs, it might be a captive portal
            if response.status_code in (301, 302, 307, 308):
                logging.warning(f"Internet check ({label}) resulted in redirect to {response.headers.get('Location')}. Likely captive portal.")
                return False # Treat redirect as no direct internet / captive portal

        except requests.RequestException as e:
            logging.warning(f"Internet check ({label}) failed for {url}: {e}")

    logging.info("No endpoint confirmed a direct internet connection. Possible captive portal or network issue.")
    return False


def try_login(locations: Dict[str, str], username: str, password: str,
              color_success, color_error, color_warning, color_reset,
              force: bool = False, specific_location_to_try: Optional[str] = None) -> Tuple[str, Optional[str]]:
    """
    Attempts to log in to the Praticelli network.
    If specific_location_to_try is provided, only that location (if in locations) will be attempted.
    Otherwise, iterates through locations until one is found reachable.

    Returns a tuple: (status_code_string, location_name_if_applicable)
    """
    if not username or not password:
        print(f"\n{color_error}Username o password non forniti.{color_reset}")
        logging.error("Login attempt with missing username or password.")
        return MISSING_CREDENTIALS, None

    if not force and check_internet_connection():
        print(f"\n{color_success}==================================={color_reset}")
        print(f"{color_success}Risulti già connesso a Internet.{color_reset}")
        print(f"{color_success}Usa 'f' per forzare un nuovo login.{color_reset}")
        print(f"{color_success}==================================={color_reset}\n")
        return ALREADY_CONNECTED, None

    headers = { # ... (same headers) ...
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "X-Snwl-Timer": "no-reset",
        "X-Snwl-Api-Scope": "extended"
    }
    auth_data = {"override": False, "snwl": True}

    print(f"\n{color_success}===== Tentativo di Connessione ====={color_reset}")
    logging.info(f"Starting login for user. Forced: {force}. Specific location: {specific_location_to_try}")

    locations_to_iterate = locations
    if specific_location_to_try and specific_location_to_try in locations:
        locations_to_iterate = {specific_location_to_try: locations[specific_location_to_try]}
        logging.info(f"Attempting only specific location: {specific_location_to_try}")
    elif specific_location_to_try:
        logging.warning(f"Specific location {specific_location_to_try} not found in locations list. Iterating all.")


    for location_name, base_url in locations_to_iterate.items():
        login_url = f"{base_url}/api/sonicos/auth"
        check_reach_url = f"{base_url}/sonicui/7/login/"

        print(f"Tentativo su {location_name} ({base_url})... ", end="")
        logging.info(f"Attempting GET for reachability at {location_name} ({check_reach_url})")
        
        try:
            # 1. Reachability check (GET)
            response_reach = requests.get(check_reach_url, timeout=LOGIN_SERVER_REACH_TIMEOUT, verify=False)
            if response_reach.status_code != 200:
                print(f"{color_error}Server non raggiungibile (status GET: {response_reach.status_code}){color_reset}")
                logging.warning(f"{location_name}: GET failed with status {response_reach.status_code}")
                if specific_location_to_try: # If trying specific and it fails GET, then it's NO_LOCATION_REACHABLE overall
                    return NO_LOCATION_REACHABLE, location_name
                continue # Try next location if iterating

        except requests.exceptions.RequestException as e_get:
            print(f"{color_error}Server non raggiungibile (errore GET: {type(e_get).__name__}){color_reset}")
            logging.warning(f"{location_name}: GET failed: {e_get}")
            if specific_location_to_try:
                return NO_LOCATION_REACHABLE, location_name
            continue # Try next location if iterating
        
        # If we reach here, GET for 'location_name' was successful. Now attempt POST.
        logging.info(f"GET successful for {location_name}. Proceeding to POST auth.")
        try:
            auth_response = requests.post(
                login_url, headers=headers, auth=(username, password),
                json=auth_data, timeout=LOGIN_AUTH_TIMEOUT, verify=False
            )
            logging.info(f"POST Response from {location_name}: Status {auth_response.status_code}, Body: {auth_response.text[:200]}")

            if auth_response.status_code == 200:
                print(f"{color_success}OK (200){color_reset}, verifico connessione internet effettiva... ", end="")
                time.sleep(2)
                if check_internet_connection():
                    print(f"{color_success}CONNESSO!{color_reset}")
                    logging.info(f"Successfully logged in at {location_name}. Internet confirmed.")
                    print(f"{color_success}==================================={color_reset}\n")
                    return LOGIN_SUCCESSFUL, location_name
                else:
                    print(f"{color_error}Login OK (200) ma NESSUNA connessione Internet rilevata dopo.{color_reset}")
                    logging.warning(f"Login at {location_name} (200) but internet check failed.")
                    return REACHABLE_AUTH_OK_NO_INTERNET, location_name

            elif auth_response.status_code == 401:
                username_hint = username[:3] + '***' + username[-3:] if len(username) > 5 else username[:3] + '***'
                print(f"{color_warning}Fallito (401 Unauthorized).{color_reset}")
                print(f"{color_warning}  Possibili cause per l'utente '{username_hint}':{color_reset}")
                print(f"{color_warning}    1. Credenziali effettivamente errate.{color_reset}")
                print(f"{color_warning}    2. Sessione precedente attiva/bloccata sul server Praticelli.{color_reset}")
                print(f"{color_warning}  Se le credenziali sono corrette, prova a forzare il login ('f') o attendi.{color_reset}")
                logging.warning(f"Login failed at {location_name} for user: 401 Unauthorized.")
                return REACHABLE_AUTH_FAILED_401, location_name # Crucially, return this status and location
            
            else: # Other non-200, non-401 POST errors
                print(f"{color_error}Fallito (status POST: {auth_response.status_code}).{color_reset}")
                logging.warning(f"Login (POST) failed at {location_name}: Status {auth_response.status_code}")
                return REACHABLE_POST_ERROR, location_name

        except requests.exceptions.RequestException as e_post: # Timeout, ConnectionError for POST
            print(f"{color_error}Errore durante il login (POST {type(e_post).__name__}).{color_reset}")
            logging.warning(f"POST failed at {location_name}: {e_post}")
            return REACHABLE_POST_ERROR, location_name # Still, the location was reachable by GET

    # If loop finishes, it means no location's GET was successful (if iterating all)
    print(f"\n{color_error}Nessuna sede sembra raggiungibile dopo aver provato tutte quelle configurate.{color_reset}")
    print(f"{color_error}==================================={color_reset}\n")
    logging.warning("All locations iterated, none were reachable via GET.")
    return NO_LOCATION_REACHABLE, None