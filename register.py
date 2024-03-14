from flask import Blueprint, request, jsonify, session as flask_session
from model import User, Session
from sqlalchemy.exc import SQLAlchemyError
import re
import logging

SERVICE_ACTIVATION_KEYWORD = "PENZI"
SMS_SHORTCODE = "22141"

register_blueprint = Blueprint('register', __name__)

# Initialize SQLAlchemy session
session = Session()

# Define a function to validate the format of the contact number
def validate_contact_number(contact_number):
    contact_number_pattern = re.compile(r'^\d{10}$')  # Assuming contact number is a 10-digit numeric string
    return bool(contact_number_pattern.match(contact_number))

def register_user(name, age, gender, county, town, contact_number):
    logging.info("Registering user: %s, %s, %s, %s, %s, %s", name, age, gender, county, town, contact_number)
    try:
        # Create and add the user to the database
        user = User(name=name, age=age, gender=gender, county=county, town=town, contact_number=contact_number)
        session.add(user)
        session.commit()  # Commit the changes to the database
        logging.info("User registered successfully: %s", user)
        return user.id  # Return the ID of the registered user
    except SQLAlchemyError as e:
        session.rollback()  # Rollback the changes in case of an error
        logging.error("Error occurred during database commit: %s", e)
        # You can raise a custom exception or return an error response here

@register_blueprint.route('/register', methods=['POST'])
def handle_initial_registration():
    data = request.get_json()
    sms_text = data.get('text', '') 

    if SERVICE_ACTIVATION_KEYWORD.lower() in sms_text.lower():  # Check both lowercase and uppercase
        response_message = "Welcome to our dating service with 6000 potential dating partners!\n"
        response_message += "To register, SMS start#name#age#gender#county#town#contact_number to 22141."
        return jsonify({"message": response_message})

    if sms_text.startswith("start#"):
        registration_data = sms_text.split("#")[1:]
        
        if len(registration_data) < 6:
            return jsonify({"error": "Incomplete registration. Please provide all required details."}), 400
        
        name, age, gender, county, town, contact_number = registration_data[:6]

        # Validate age
        try:
            age = int(age)
            if age <= 0:
                return jsonify({"error": "Age must be a positive integer."}), 400
        except ValueError:
            return jsonify({"error": "Age must be a valid integer."}), 400

        # Validate gender
        allowed_genders = ['male', 'female']
        if gender.lower() not in allowed_genders:
            return jsonify({"error": f"Gender must be one of: {', '.join(allowed_genders)}"}), 400

        # Validate contact number format
        if not validate_contact_number(contact_number):
            return jsonify({"error": "Invalid contact number format. It must be a 10-digit numeric string."}), 400

        # Register the user with default contact number
        register_user(name, int(age), gender, county, town, contact_number)

        # Prompt user to provide additional details
        response_message = "Would you like to provide additional details?"
        return jsonify({"message": response_message})

    return jsonify({"error": "Invalid command."}), 400

# Other routes and functions...



@register_blueprint.route('/additional-details', methods=['POST'])
def handle_additional_details():
    data = request.get_json()
    sms_text = data.get('text', '')

    if sms_text.lower() == "yes":
        # Provide the user with the format for providing additional details
        response_message = "SMS details#levelOfEducation#profession#maritalStatus#religion#ethnicity to 22141.\n"
        response_message += "E.g. details#diploma#driver#single#christian#mijikenda"
        return jsonify({"message": response_message})
    
    elif sms_text.lower() == "no":
        # If user doesn't provide additional details, respond with a message indicating the registration is complete
        return jsonify({"message": "You were registered for dating with your initial details.\nTo search for a MPENZI, SMS match#age#town to 22141 and meet the person of your dreams.\nE.g., match#23-25#Nairobi"})

    elif sms_text.startswith("details#"):
        additional_details = sms_text.split("#")[1:]
        if len(additional_details) != 5:
            return jsonify({"error": "Invalid command. Please provide all required additional details."}), 400
            
        user = session.query(User).order_by(User.id.desc()).first()  # Get the last registered user
        if user:
            user.level_of_education = additional_details[0]
            user.profession = additional_details[1]
            user.marital_status = additional_details[2]
            user.religion = additional_details[3]
            user.ethnicity = additional_details[4]
            session.commit()
            return jsonify({"message": "This is the last stage of registration\nSMS a brief description of yourself to 22141 starting with the word MYSELF E.g., MYSELF chocolate, lovely, sexy etc"})
        else:
            return jsonify({"error": "No user found. Please register first."}), 400

    else:
        return jsonify({"error": "Invalid command. Please respond with 'yes' or 'no'."}), 400

@register_blueprint.route('/final-registration', methods=['POST'])
def handle_final_registration():
    data = request.get_json()
    sms_text = data.get('text', '') 

    if sms_text.startswith("MYSELF"):
        description = sms_text.split("MYSELF", 1)[-1].strip()
        # Process and save self-description
        user = session.query(User).order_by(User.id.desc()).first()
        if user:
            user.self_description = description
            session.commit()
            return jsonify({"message": "You are now registered for dating\nTo search for a MPENZI, SMS match#age#town to 22141 and meet the person of your dreams"})
        else:
            return jsonify({"error": "No user found. Please register first."}), 400
    else:
        return jsonify({"error": "Invalid command. Please start your message with 'MYSELF'."}), 400

