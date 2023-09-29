# Import Library
from flask import Flask, jsonify, request, render_template
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from
from datetime import datetime

import os

# app definition
app = Flask(__name__)
# database config
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:mSVCivGq4m22uLGjZLKD@containers-us-west-204.railway.app:8059/railway'


# if __name__ == '__main__':
#     app.run(debug=True, port=5030)

if __name__ == '__main__':
    app.run(debug=True)
