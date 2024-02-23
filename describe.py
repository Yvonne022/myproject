from flask import Blueprint, jsonify, request
from model import User, Session

describe_blueprint = Blueprint('describe', __name__)

@describe_blueprint.route('/describe', methods=['POST'])
def describe():
    phone_number = request.form.get('text')
    if phone_number is None:
        return "Invalid request. 'phone_number' parameter is missing.", 400

    user = query_user_by_contact_number(phone_number)
    if user is None:
        return f"No user found with the phone number {phone_number}.", 404

    # Format the user details
    user_details = f"{user.name} aged {user.age}, {user.county} County, {user.town} town, {user.level_of_education}, {user.profession}, {user.marital_status}, {user.religion}, {user.ethnicity}."

    # Include the instruction to describe another user
    user_details += f" Send DESCRIBE {user.contact_number} to get more details about {user.name}."

    # Send the response
    # Note: Modify this part according to how you are sending responses (e.g., via SMS)
    return user_details

def query_user_by_contact_number(phone_number):
    # Create a session instance
    session = Session()

    # Query user by contact number
    user = session.query(User).filter(User.contact_number == phone_number).first()

    session.close()  # Close the session

    return user
