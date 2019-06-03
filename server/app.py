#Main application
##TODO: Seperate into different files/modules

#Imports
from flask import Flask, request, jsonify, abort, Response, g
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask_httpauth import HTTPBasicAuth
from datetime import datetime
import os
                  
#Init
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SECRET_KEY'] = 'CHANGEMELATER'

#Extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
db.init_app(app)
db.create_all()

#Models
class Message(db.Model):
  __tablename__ = 'messages'
  id = db.Column(db.Integer, primary_key = True)
  sender = db.Column(db.Integer)
  recipient = db.Column(db.Integer)
  content = db.Column(db.String(128))
  timestamp = db.Column(db.DateTime)
  saved = db.Column(db.Boolean)
  edited = db.Column(db.Boolean)
  deleted = db.Column(db.Boolean)

  def __init__(self, sender, recipient, message):
    self.sender = sender
    self.recipient = recipient
    self.content = message
    self.timestamp = datetime.now()
    self.edited = False
    self.saved = False
    self.deleted = False

  def edit(self, message):
    self.edited = True
    self.content = message
  
  def delete(self):
    self.deleted = True
    self.content = "This message has been deleted."
  
  def serialize(self):
    return {
      'sender': self.sender,
      'recipient': self.recipient,
      'content': self.content,
      'timestamp': self.timestamp,
      'saved': self.saved,
      'edited': self.edited,
      'deleted': self.deleted
    }

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(32), index = True, unique = True)
  password_hash = db.Column(db.String(128))

  def hash_password(self, password):
    self.password_hash = pwd_context.encrypt(password)
  
  def verify_password(self, password):
    return pwd_context.verify(password, self.password_hash)

  def generate_auth_token(self, expiration=600):
    s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
    return s.dumps({'id': self.id})
  
  @staticmethod
  def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
      data = s.loads(token)
    except SignatureExpired:
      return None #Valid token, but expired
    except BadSignature:
      return None #Invalid token
    user = User.query.get(data['id'])
    return user
  
  def serialize(self):
    return {
      'username': self.username
    }

#Routes
@app.route('/')
def hello_world():
  return "Hello world"

@app.route('/users', methods=['POST'])
def new_user():
  username = request.json.get('username')
  password = request.json.get('password')
  if username is None or password is None:
    abort(400) # missing arguments
  if User.query.filter_by(username = username).first() is not None:
    abort(409) # user already exists
    abort(Response("User already exists"))
  user = User(username = username)
  user.hash_password(password)
  db.session.add(user)
  db.session.commit()
  return jsonify({'username': user.username}), 201

@app.route('/token')
@auth.login_required
def get_auth_token():
  token = g.user.generate_auth_token()
  return jsonify({'token': token.decode('ascii')})

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/messages')
@auth.login_required
def get_my_messages():
  recieved = Message.query.filter_by(recipient = g.user.id).all()
  return jsonify(messages = [m.serialize() for m in recieved])

@app.route('/messages/<id>')
@auth.login_required
def get_messages_from_contact(id):
   recieved = [m.serialize() for m in Message.query.filter_by(recipient = g.user.id).all()]
   sent = [m.serialize() for m in Message.query.filter_by(sender = g.user.id).all()]
   messages = sent + recieved
   messages.sort(key=lambda m: m['timestamp'])
   return jsonify({'messages': messages})

@app.route('/messages/<id>', methods=['POST'])
@auth.login_required
def send_message(id):
   message = Message(g.user.id, id, request.json.get('message'))
   db.session.add(message)
   db.session.commit()
   return jsonify({'message': message.serialize()})

@app.route('/users')
@auth.login_required
def get_users():
  users = [u.serialize() for u in User.query.all()]
  return jsonify({'users': users})
  
@app.route('/users/<username>')
def get_user_id(username):
  user = User.query.filter_by(username=username).first()
  return jsonify({'id': user.id})

if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)