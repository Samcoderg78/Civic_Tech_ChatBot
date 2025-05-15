import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'safety_bot.db')

# Redis configuration (for scaling to 870k users)
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Bait car API configuration
BAIT_CAR_API_URL = os.environ.get('BAIT_CAR_API_URL', 'https://api.impd.gov/baitcars')
BAIT_CAR_API_KEY = os.environ.get('BAIT_CAR_API_KEY')

# NHTSA API configuration
NHTSA_API_URL = os.environ.get('NHTSA_API_URL', 'https://vpic.nhtsa.dot.gov/api/vehicles')

# Report retention period (in hours)
REPORT_RETENTION_HOURS = 48

# Debug mode
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'

# Directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)