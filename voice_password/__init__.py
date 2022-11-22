from flask import Flask

app = Flask(__name__)

from voice_password import routes, mainRoute
