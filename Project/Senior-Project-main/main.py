from website import create_app
from dotenv import load_dotenv
# from pyngrok import ngrok, conf
import os

# Load environment variables
load_dotenv()

# Optional: configure auth token (only needed once)
# conf.get_default().auth_token = os.getenv("NGROK_AUTH_TOKEN", "2zpgoxXBYs7x0z1NhGAWvYETYiO_5xcwWhgWeeCk7iuZY7TZT")

class Config:
    def __init__(self):
        self._secret_key = os.getenv('SECRET_KEY', 'ThisiSAr@nDomsEcRetEKey21')
    
    def get_secret_key(self): 
        return self._secret_key

config = Config()
app = create_app(config.get_secret_key())

if __name__ == '__main__':
    app.run(debug=True, port=5000)

