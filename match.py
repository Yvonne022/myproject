from flask import Blueprint, jsonify, request
from model import User, Session

match_blueprint = Blueprint('match', __name__)

@match_blueprint.route('/match', methods=['POST'])
def match():
    # Receive and process matching request from SMS
    sms_content = request.form.get('text')  
    if sms_content is None:
        return "Invalid request. 'text' parameter is missing.", 400

    age_range, town = extract_matching_criteria(sms_content)

    if not age_range or not town:
        return "Incomplete or invalid matching criteria. Please provide both age range and town in the format 'match#age_range#town'.", 400

    # Query database for matching users
    matches = query_matching_users(age_range, town)

    if not matches:
        return "No matching users found.", 404

    # Send matching user details back to the sender via SMS
    response = send_matching_user_details(matches)


    return response, 200


@match_blueprint.route('/user-details', methods=['POST'])

def user_details():
    sms_text = request.form.get('text')
    if sms_text is None:
        return "Invalid request. 'text' parameter is missing.", 400

    if sms_text.startswith('DESCRIBE'):
        phone_number = sms_text.split()[1]  # Extract the phone number from the command
        # Query database for user details
        user = query_user_by_phone_number(phone_number)

        if user is None:
            return "User not found.", 404

        # Check if user has provided self-description
        if user.self_description:
            return f"{user.name} describes themselves as {user.self_description}.", 200
        else:
            return f"{user.name} has not provided a self-description.", 200

    # If not 'DESCRIBE', return basic user details
    phone_number = sms_text.strip()  # Assuming the phone number is directly provided in the text

    # Query database for user details
    user = query_user_by_phone_number(phone_number)

    if user is None:
        return "User not found.", 404

    # Format and return user details
    response = f"{user.contact_number}\n"
    response += f"{user.name} aged {user.age}, {user.county} County, {user.town} town, {user.level_of_education}, {user.profession}, {user.marital_status}, {user.religion}, {user.ethnicity}.\n"
    response += f"Send DESCRIBE {user.contact_number} to get more details about {user.name}"

    return response, 200


def extract_matching_criteria(sms_content):
    # Extract age range and town from SMS content
    # Example: match#26-30#Nairobi
    if sms_content is None:
        return None, None
    parts = sms_content.split('#')
    if len(parts) != 3 or parts[0] != 'match':
        return None, None

    age_range = parts[1]
    town = parts[2]

    # Validate age range format
    min_age, max_age = age_range.split('-')
    try:
        min_age = int(min_age)
        max_age = int(max_age)
    except ValueError:
        return None, None

    return age_range, town

def query_matching_users(age_range, town):
    min_age, max_age = parse_age_range(age_range)

    # Create a session instance
    session = Session()

    # Query matching users
    matches = session.query(User).filter(
        User.age >= min_age,
        User.age <= max_age,
        User.town == town
    ).limit(32).all()  # Limit to 32 users

    session.close()  # Close the session

    return matches

def parse_age_range(age_range):
    min_age, max_age = age_range.split('-')
    return int(min_age), int(max_age)

def send_matching_user_details(matches, requester_name, requester_age,requester_county):
    # Format and send details of matching users
    response = f"We have {len(matches)} ladies who match your choice! We will send you details of {len(matches)} of them shortly.\n"
    response += f"To get more details about them, SMS their number e.g., {matches[0].contact_number} to 22141\n"
    # Format details of matching users (limit to 3)
    for user in matches[:3]:
        response += f"{user.name} aged {user.age}, {user.contact_number}.\n"

    if len(matches) > 3:
        response += f"Send NEXT to 22141 to receive details of the remaining {len(matches) - 3} ladies"

    response += f"\n{requester_name}, aged {requester_age}, is interested in you and requested your details.\n"
    response += f"He is based in {requester_county}.\n"
    response += "Do you want to know more about him? Send YES to 22141"


    # Send the response
    # Note: Modify this part according to how you are sending responses (e.g., via SMS)
    return response

def query_user_by_phone_number(phone_number):
    session = Session()
    user = session.query(User).filter(User.contact_number == phone_number).first()
    session.close()
    return user
