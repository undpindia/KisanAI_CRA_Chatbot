# Local Application/Library Imports
from app.src.handlers.state_manager import AppState
from app.src.wrappers.whatsapp_wrapper import WhatsApp

# Initialize state first
state = AppState()

# Initialize messenger after settings are loaded
def get_messenger():
    return WhatsApp()

messenger = get_messenger()

# Add a refresh method if needed
def refresh_instances():
    global messenger
    messenger = WhatsApp()
