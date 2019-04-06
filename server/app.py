from flask import Flask, request, jsonify, abort, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask_httpauth import HTTPBasicAuth
                  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

#Extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(32), index = True)
  password_hash = db.Column(db.String(128))

  def hash_password(self, password):
    self.password_hash = pwd_context.encrypt(password)
  
  def verify_password(self, password):
    return pwd_context.verify(password, self.password_hash)

  def generate_auth_token(self, expiration=600):
    s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
    return s.dumps({id: self.id})
  
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
@auth.login_required()
def get_auth_token():
  token = g.user.generate_auth_token()
  return jsonify({'token': token.decode('ascii')}), 201

