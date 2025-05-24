# config_manager.py
import os
import configparser
import logging
from constants import CONFIG_FILE, DEFAULT_USERNAME_PLACEHOLDER

def create_default_config():
    """Creates a default configuration file."""
    config = configparser.ConfigParser()
    config['GeneralSettings'] = {
        'Username': DEFAULT_USERNAME_PLACEHOLDER, # Store username for keyring, not a secret itself
        'HasFirstRun': 'true', # Set to true, main logic will handle first-time credential input
        'LastConnectedLocation': ''
    }
    config['Locations'] = {
        'viola': 'https://sw-prviola.unipi.it:444',
        'blu': 'https://sw-prblu.unipi.it:444',
        'verde': 'https://sw-prverde.unipi.it:444',
        'giallo': 'https://sw-prgiallo.unipi.it:444',
        'arancio': 'https://sw-prarancio.unipi.it:444',
        'rosso': 'https://sw-prrosso.unipi.it:444'
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    logging.info(f"Default config file created at {CONFIG_FILE}")
    return config

def load_config() -> tuple[configparser.ConfigParser, bool]:
    """Loads configuration. Returns config object and a boolean indicating if it was the first run (based on content)."""
    config = configparser.ConfigParser()
    is_newly_created = False
    if not os.path.exists(CONFIG_FILE):
        config = create_default_config()
        is_newly_created = True # A default config is created, effectively a first run state for setup

    config.read(CONFIG_FILE)

    # Ensure sections and keys exist, add if missing (migration for older configs)
    if 'GeneralSettings' not in config:
        config['GeneralSettings'] = {}
        is_newly_created = True # Treat as first run if critical section missing
    if 'Username' not in config['GeneralSettings']:
        config['GeneralSettings']['Username'] = DEFAULT_USERNAME_PLACEHOLDER
        is_newly_created = True
    if 'HasFirstRun' not in config['GeneralSettings']:
        config['GeneralSettings']['HasFirstRun'] = 'true' # Default to true, prompt for creds if user/pass missing
        is_newly_created = True
    if 'LastConnectedLocation' not in config['GeneralSettings']:
        config['GeneralSettings']['LastConnectedLocation'] = ''

    if 'Locations' not in config:
        config['Locations'] = {
            'viola': 'https://sw-prviola.unipi.it:444',
            'blu': 'https://sw-prblu.unipi.it:444',
            'verde': 'https://sw-prverde.unipi.it:444',
            'giallo': 'https://sw-prgiallo.unipi.it:444',
            'arancio': 'https://sw-prarancio.unipi.it:444',
            'rosso': 'https://sw-prrosso.unipi.it:444'
        }
        is_newly_created = True

    if is_newly_created: # Save if we modified it or created it
        save_config(config)

    # First run is true if 'HasFirstRun' is explicitly true in config
    # OR if username is still the placeholder (meaning setup wasn't completed)
    is_first_run_logic = config.getboolean('GeneralSettings', 'HasFirstRun', fallback=True) or \
                         config['GeneralSettings']['Username'] == DEFAULT_USERNAME_PLACEHOLDER

    return config, is_first_run_logic


def save_config(config: configparser.ConfigParser):
    """Saves the configuration object to the file."""
    try:
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        logging.info("Configuration saved.")
    except IOError as e:
        logging.error(f"Error saving configuration file: {e}")

def get_username_from_config(config: configparser.ConfigParser) -> str:
    """Gets the stored username from config."""
    return config.get('GeneralSettings', 'Username', fallback=DEFAULT_USERNAME_PLACEHOLDER)

def store_username_in_config(config: configparser.ConfigParser, username: str):
    """Stores the username in the config file."""
    if 'GeneralSettings' not in config:
        config['GeneralSettings'] = {}
    config['GeneralSettings']['Username'] = username
    save_config(config)
    logging.info(f"Username '{username}' stored in config.")

def mark_first_run_completed(config: configparser.ConfigParser):
    """Marks that the first run setup has been completed."""
    if 'GeneralSettings' not in config:
        config['GeneralSettings'] = {}
    config['GeneralSettings']['HasFirstRun'] = 'false'
    save_config(config)
    logging.info("First run status updated to completed.")

def get_last_location(config: configparser.ConfigParser) -> str:
    """Gets the last connected location from config."""
    return config.get('GeneralSettings', 'LastConnectedLocation', fallback='')

def update_last_location(config: configparser.ConfigParser, location: str | None): # Allow None
    """Updates the last connected location in the config file."""
    if 'GeneralSettings' not in config:
        config['GeneralSettings'] = {}
    
    # Ensure location is a string, even if None is passed
    config['GeneralSettings']['LastConnectedLocation'] = location if location is not None else ''
    
    save_config(config)
    logging.info(f"Last connected location updated to: '{config['GeneralSettings']['LastConnectedLocation']}'")

def get_locations(config: configparser.ConfigParser) -> dict:
    """Gets the dictionary of locations and their URLs."""
    if 'Locations' in config:
        return dict(config.items('Locations'))
    return {}