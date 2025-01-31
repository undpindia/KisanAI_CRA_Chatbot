import logging
import os

# Ensure the logs directory exists
os.makedirs('whatsapp_bot/app/logs', exist_ok=True)

# Configure the logger
logging.basicConfig(
    filename='whatsapp_bot/app/logs/app.log',
    level=logging.DEBUG,  # You can change this to INFO or ERROR as needed
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create a logger instance
logger = logging.getLogger('whatsapp_bot') 