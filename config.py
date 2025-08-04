import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # IBM Watson Assistant
    IBM_API_KEY = os.getenv('IBM_API_KEY')
    IBM_ASSISTANT_ID = os.getenv('IBM_ASSISTANT_ID')
    IBM_SERVICE_URL = os.getenv('IBM_SERVICE_URL', 'https://api.us-south.assistant.watson.cloud.ibm.com')
    IBM_PROJECT_ID = os.getenv('IBM_PROJECT_ID')
    IBM_VERSION = '2023-06-15'
    
    # External APIs (optional)
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    MAPS_API_KEY = os.getenv('MAPS_API_KEY')
    
    # App Configuration
    APP_TITLE = "AI Travel Planner"
    APP_ICON = "✈️"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = ['IBM_API_KEY', 'IBM_ASSISTANT_ID']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True