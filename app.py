import logging
from flask import Flask, jsonify, request, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static')

app.secret_key = "1234"
logging.basicConfig(level=logging.DEBUG)

CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'
db = SQLAlchemy(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import routes and models
from register import register_blueprint
from match import get_current_user_id, match_blueprint
from message import message_blueprint

# Register blueprints
app.register_blueprint(register_blueprint)
app.register_blueprint(match_blueprint)  
app.register_blueprint(message_blueprint)

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

# Route to render index.html
@app.route('/')
def index():
    return render_template('index.html')

# Route to render activation.html
@app.route('/activation')
def activation():
    return render_template('activation.html')

#Route to render match.html
@app.route('/match')
def match():
    user_id = get_current_user_id()
    return render_template('match.html', user_id=user_id)

@app.route('/express-interest')
def express_interest():
    return render_template('interest.html')


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8000)
