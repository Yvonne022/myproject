from flask import request
from model import Session, User
from flask import app

@app.route('/additional-details', methods=['POST'])
def submit_additional_details():
    data = request.form
    user_id = data.get('user_id')
    level_of_education = data.get('level_of_education')
    profession = data.get('profession')
    marital_status = data.get('marital_status')
    religion = data.get('religion')
    ethnicity = data.get('ethnicity')

    session = Session()
    user = session.query(User).get(user_id)
    if user:
        user.level_of_education = level_of_education
        user.profession = profession
        user.marital_status = marital_status
        user.religion = religion
        user.ethnicity = ethnicity
        session.commit()
        session.close()
        return "Additional details updated successfully", 200
    else:
        session.close()
        return "User not found", 404
