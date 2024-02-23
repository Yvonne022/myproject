from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from match import match_blueprint

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db' 

# Initialize database
db = SQLAlchemy(app)

# Import routes
from register import register_blueprint
from match import match_blueprint 
from message import message_blueprint
from describe import describe_blueprint

# Register blueprints
app.register_blueprint(register_blueprint)
app.register_blueprint(match_blueprint)  
app.register_blueprint(message_blueprint)
app.register_blueprint(describe_blueprint)


# Error handlers
@app.errorhandler(404)
def not_found(e):
  return "Not found", 404

@app.errorhandler(400)  
def bad_request(e):
  return "Bad request", 400

# Configure JSON request parsing  
@app.before_request
def before_request():
  if request.content_type == 'application/json':
        request.parsed_json = request.get_json()






# Run the app
if __name__ == '__main__':
  app.run(debug=True)