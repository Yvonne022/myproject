from flask import Blueprint, request, jsonify, session
from model import User, Session
import logging

match_blueprint = Blueprint('match', __name__)

@match_blueprint.route('/match', methods=['POST'])
def match():
    data = request.get_json()
    sms_content = data.get('text')
    
    if sms_content is None :
        return jsonify({"error": "Invalid request. 'text'  is missing."}), 400

    age_range, town = extract_matching_criteria(sms_content)

    if not age_range or not town:
        return jsonify({"error": "Incomplete or invalid matching criteria. Please provide both age range and town in the format 'match#age_range#town'."}), 400

    # Query database for matching users, excluding the current user
    matches = query_matching_users(age_range, town,)

    if not matches:
        return jsonify({"message": "No matching users found."}), 404

    # Format matching user details as HTML <a> tags
    response = f"We have {len(matches)} matching users who match your choice! We will send you details of {len(matches)} of them shortly.<br>"
    response += "To get more details about them, click on their name.<br>"
    for user in matches:
        response += f"<a href='#' class='user-details' data-phone-number='{user.contact_number}'>{user.name} aged {user.age}</a><br>"

    return jsonify({"message": response}), 200

@match_blueprint.route('/user-details', methods=['POST'])
def user_details():
    data = request.get_json()
    sms_content = data.get('text')
    if sms_content is None:
        return jsonify({"error": "Invalid request. 'text' parameter is missing."}), 400

    parts = sms_content.split()
    if len(parts) == 2 and parts[0] == 'DESCRIBE':
        phone_number = parts[1]
        user = query_user_by_phone_number(phone_number)

        if user is None:
            return jsonify({"message": "User not found."}), 404

        # Construct the user details message
        user_details = f"{user.contact_number} {user.name} aged {user.age}, {user.gender}, {user.county} County, {user.town} Town."

        # Check for additional details
        if any([user.level_of_education, user.profession, user.marital_status, user.religion, user.ethnicity]):
            user_details += f" {user.level_of_education}, {user.profession}, {user.marital_status}, {user.religion}, {user.ethnicity}."
        
        # Add self-description if available, otherwise indicate it's not provided
        if user.self_description:
            user_details += f" {user.self_description}"
        else:
            user_details += f" {user.name} has not provided a self-description."

        # Add instructions to get more details
        user_details += f" Send DESCRIBE {user.contact_number} to get more details about {user.name}"

        return jsonify({"details": user_details}), 200

    # If not a DESCRIBE command, assume it's a request for basic user details
    phone_number = sms_content.strip()  

    # Query database for user details
    user = query_user_by_phone_number(phone_number)

    if user is None:
        return jsonify({"message": "User not found."}), 404

    # Construct the basic user details message
    user_details = f"{user.contact_number} {user.name} aged {user.age}, {user.gender}, {user.county} County, {user.town} Town."

    # Check for additional details
    if any([user.level_of_education, user.profession, user.marital_status, user.religion, user.ethnicity]):
        user_details += f" {user.level_of_education}, {user.profession}, {user.marital_status}, {user.religion}, {user.ethnicity}."

    # Add instructions to get more details
    user_details += f" Send DESCRIBE {user.contact_number} to get more details about {user.name}"

    return jsonify({"details": user_details}), 200


@match_blueprint.route('/describe', methods=['POST'])
def describe_user():
    data = request.get_json()
    sms_content = data.get('text')

    if sms_content is None or not sms_content.startswith('DESCRIBE'):
        return jsonify({"error": "Invalid request. 'text' parameter must start with 'DESCRIBE'."}), 400

    parts = sms_content.split()
    if len(parts) != 2:
        return jsonify({"error": "Invalid request. 'text' parameter must contain a phone number."}), 400

    phone_number = parts[1]
    user = query_user_by_phone_number(phone_number)

    if user is None:
        return jsonify({"message": "User not found"}), 404

    if user.self_description:
        return jsonify({"description": f"{user.name} describes themselves as {user.self_description}."}), 200
    else:
        return jsonify({"message": f"{user.name} has not provided a self-description."}), 200


@match_blueprint.route('/express-interest', methods=['POST'])
def express_interest():
    data = request.get_json()
    sms_content = data.get('text')
    
    if sms_content is None:
        return jsonify({"error": "Invalid request. 'text' parameter is missing."}), 400

    if sms_content.strip().upper() == 'YES':
        # Fetch the details of the requester here
        requester_name = data.get('requester_name')  # Assuming requester's name is provided in the request
        requester_details = query_user_by_name(requester_name)  # Fetch requester's details

        if requester_details:
            # Construct response message with requester's details
            response_message = f"{requester_details.name}, {requester_details.gender} aged {requester_details.age}, {requester_details.county} County, {requester_details.town} town, {requester_details.contact_number}"
            if requester_details.level_of_education != 'None':
                response_message += f", {requester_details.level_of_education}"
            if requester_details.profession != 'None':
                response_message += f", {requester_details.profession}"
            if requester_details.marital_status != 'None':
                response_message += f", {requester_details.marital_status}"
            if requester_details.religion != 'None':
                response_message += f", {requester_details.religion}"
            if requester_details.ethnicity != 'None':
                response_message += f", {requester_details.ethnicity}"
            response_message += ".\n"
            response_message += f"Do you want to know more about them? Send YES to 22141\n"
            return jsonify({"message": response_message}), 200
        else:
            return jsonify({"error": "Requester details not found."}), 404

    # Remaining code for handling other cases...

    
    # This block handles the case where the request is made to express interest in the specified person
    parts = sms_content.split(',')
    if len(parts) == 2:
        requested_person_name = parts[0].strip()
        requester_name = parts[1].strip()

        # Fetch requester details again
        requester_details = query_user_by_name(requester_name)

        if requester_details:
            # Construct response message without requester details
            response_message = f"Hi {requested_person_name}, {requester_name} is interested in you and requested your details.\n"
            response_message += f"They are aged {requester_details.age} based in {requester_details.county} County, {requester_details.town}.\n"
            response_message += f"Do you want to know more about them? Send YES to 22141\n"

            return jsonify({"message": response_message}), 200
        else:
            return jsonify({"error": f"Requester {requester_name} details not found."}), 404

    return jsonify({"error": "Invalid request. Please provide 'YES' or the names of the requested person and the requester separated by commas."}), 400

def send_matching_user_details(matches, requester_gender=None, requester_name=None, requester_age=None):
    # Determine the gender text based on the provided requester's gender
    if requester_gender == "male":
        gender_text = "ladies"
    elif requester_gender == "female":
        gender_text = "males"
    else:
        gender_text = "matching users"

    # Format and send details of matching users
    response = f"We have {len(matches)} {gender_text} who match your choice! We will send you details of {len(matches)} of them shortly.\n"
    response += f"To get more details about them, SMS their number e.g., {matches[0].contact_number} to 22141\n"
    # Format details of matching users (limit to 3)
    for user in matches[:3]:
        response += f"{user.name} aged {user.age}, {user.contact_number}.\n"

    if len(matches) > 3:
        response += f"Send NEXT to 22141 to receive details of the remaining {len(matches) - 3} {gender_text}\n"

    if requester_name and requester_age:
        # Include information about the requester's interest
        response += f"\nHi {matches[0].name}, a {requester_gender} called {requester_name} is interested in you and requested your details.\n"
        response += f"He is aged {requester_age}.\n"
        response += "Do you want to know more about him? Send YES to 22141\n"

    return response

def extract_matching_criteria(sms_content):
    # Extract age range and town from SMS content
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

def query_matching_users(age_range, town, ):  
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

def query_user_by_phone_number(phone_number):
    session = Session()
    user = session.query(User).filter(User.contact_number == phone_number).first()
    session.close()
    return user

def get_current_user_id():
    # Retrieve the current user's ID from the Flask session
    return session.get('user_id')

def query_user_by_name(name):

  logging.debug(f"Querying user with name: {name}")

  try:

    session = Session()

    logging.debug("Opening session")

    # Print name before passing to query
    print(f"Name passed to query: {name}")  

    user = session.query(User)

    logging.debug("Built initial query")

    # Print query object
    print(f"Query: {user}")

    user = user.filter(User.name == name).first()

    logging.debug("Applied name filter")

    # Print returned user
    if user:
      print(f"Found user: {user}")

    else: 
      print("No user found")

    session.close()

    logging.debug("Closing session")

    return user

  except Exception as e:

    logging.error(f"Error querying user: {e}")

    return {"error": str(e)}

  finally:

    logging.debug("Query complete")