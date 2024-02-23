from flask import Flask, request
from model import User
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db' 

# Initialize database
db = SQLAlchemy(app)

@app.route('/details', methods=['POST'])
def details():

    data = request.form
    phone = data.get('phone')

    user = User.query.filter_by(phone=phone).first()

    if user:
        if not user.education:
            user.education = data.get('education')

        if not user.profession:  
            user.profession = data.get('profession')

        if not user.marital_status:
            user.marital_status = data.get('marital_status')

        if not user.religion:  
            user.religion = data.get('religion')

        if not user.ethnicity:
            user.ethnicity = data.get('ethnicity')

        db.session.commit()

        return "Details added! Description route..."
    else:
        return "User not found."

if __name__ == '__main__':
    app.run(debug=True)
