from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask import Flask, request
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class UserChatHistory(db.Model):
    __tablename__="existinguser"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(50))
    message = db.Column(db.String)
    

    def __init__(self, user_id, message):
        self.user_id = user_id
        self.message = message



def generate_user_id():
    # Generate a unique user ID using a combination of IP address and timestamp
    ip_address = request.remote_addr
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = f"{ip_address}_{timestamp}"
    return unique_id