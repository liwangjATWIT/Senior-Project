from website import create_app 

class Config:
    def __init__(self):
        self._secrete_key = "ThisiSAr@nDomsEcRetEKey21"
    
    def get_secrete_key(self): 
        return self._secrete_key

config = Config()
app = create_app(config.get_secrete_key())

if __name__== '__main__':
    app.run(debug=True)