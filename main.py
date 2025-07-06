from website import create_app 

class Config:
    def __init__(self):
        self._secret_key = "ThisiSAr@nDomsEcRetEKey21"
    
    def get_secret_key(self): 
        return self._secret_key

config = Config()
app = create_app(config.get_secret_key())

if __name__== '__main__':
    app.run(debug=True)