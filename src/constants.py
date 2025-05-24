# constants.py
import os

# --- DIRECTORY AND FILE PATHS ---
APP_NAME = "Fast_Pratilogin"
APP_DIR = os.path.join(os.getenv('APPDATA', ''), APP_NAME) # os.getenv default for non-Windows
EXE_NAME = "PratiLogin.exe" # Assuming it will be compiled
EXE_PATH = os.path.join(APP_DIR, EXE_NAME)
CONFIG_FILE = os.path.join(APP_DIR, "config.ini")
LOG_FILE = os.path.join(APP_DIR, "autologin.log")

# --- KEYRING ---
KEYRING_SERVICE_NAME = "FastPratilogin_UNIPI"

# --- NETWORK ---
# Increased timeouts for potentially slow captive portal networks
NETWORK_CHECK_TIMEOUT = 5  # For general internet check
LOGIN_SERVER_REACH_TIMEOUT = 0.7 # For initial GET to login server
LOGIN_AUTH_TIMEOUT = 1.5         # For POST request during login

# --- LOGGING ---
MAX_FORCE_RETRIES = 5 # Max retries for forced login
FORCE_RETRY_DELAY = 1 # Seconds

# Define status constants for try_login return
LOGIN_SUCCESSFUL = "LOGIN_SUCCESSFUL"
REACHABLE_AUTH_FAILED_401 = "REACHABLE_AUTH_FAILED_401"
REACHABLE_AUTH_OK_NO_INTERNET = "REACHABLE_AUTH_OK_NO_INTERNET"
REACHABLE_POST_ERROR = "REACHABLE_POST_ERROR" # General POST failure after successful GET
NO_LOCATION_REACHABLE = "NO_LOCATION_REACHABLE"
ALREADY_CONNECTED = "ALREADY_CONNECTED"
MISSING_CREDENTIALS = "MISSING_CREDENTIALS"

# --- OTHER ---
DEFAULT_USERNAME_PLACEHOLDER = "username_not_set"