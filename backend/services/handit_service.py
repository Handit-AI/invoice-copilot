"""
Handit.ai service initialization and configuration.
This file creates a singleton tracker instance that can be imported across your application.
"""
import os
from dotenv import load_dotenv
from handit import HanditTracker

# Load environment variables from .env file
load_dotenv()

# Create a singleton tracker instance
tracker = HanditTracker()  # Creates a global tracker instance for consistent tracing across the app

# Configure with your API key from environment variables
api_key = os.getenv("HANDIT_API_KEY")
if api_key:
    tracker.config(api_key=api_key)  # Sets up authentication for Handit.ai services
else:
    # If no API key, create a dummy tracker that does nothing
    class DummyTracker:
        def start_tracing(self, **kwargs):
            return {"executionId": "dummy"}
        
        def end_tracing(self, **kwargs):
            pass
        
        def track_node(self, **kwargs):
            pass
        
        def config(self, **kwargs):
            pass
    
    tracker = DummyTracker()