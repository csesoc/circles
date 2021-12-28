''' The central point from where we will run our server. It will open up the 
api and also run the files'''

import uvicorn
from server.server import app

if __name__ == "__main__":
    uvicorn.run(app, host='backend')
