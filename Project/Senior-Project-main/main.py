from website import create_app
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Config:
    def __init__(self):
        # Use environment variable for secret key
        self._secret_key = os.getenv('SECRET_KEY', 'ThisiSAr@nDomsEcRetEKey21')
    
    def get_secret_key(self): 
        return self._secret_key

config = Config()
app = create_app(config.get_secret_key())

if __name__== '__main__':
    app.run(debug=True)