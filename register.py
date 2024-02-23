from flask import Flask, jsonify, request
from sqlalchemy import func
from model import User, Session
from flask import Blueprint

register_blueprint = Blueprint('register', __name__)

app = Flask(__name__)
app.register_blueprint(register_blueprint)

SERVICE_ACTIVATION_KEYWORD = "PENZI"
SMS_SHORTCODE = "22141"

# Initialize SQLAlchemy session
session = Session()

def register_user(name, age, gender, county, town, contact_number):
    # Create and add the user to the database
    user = User(name=name, age=age, gender=gender, county=county, town=town, contact_number=contact_number)
    session.add(user)
    session.commit()

def process_self_description(description):
    user = session.query(User).order_by(User.id.desc()).first()
    if user:
        user.self_description = description
        session.commit()  # Commit the changes to the database

@app.route('/', methods=['POST'])
def handle_sms():
    sms_text = request.form.get('text', '')  # Do not convert to lowercase here
    print("Received SMS text:", sms_text)

    if SERVICE_ACTIVATION_KEYWORD.lower() in sms_text.lower():  # Check both lowercase and uppercase
        response_message = "Welcome to our dating service with 6000 potential dating partners!\n"
        response_message += "To register, SMS start#name#age#gender#county#town#contact_number to 22141."
        return response_message

    print("SMS text does not contain the service activation keyword.")

    if sms_text.startswith("start#"):
        registration_data = sms_text.split("#")[1:]
        
        if len(registration_data) < 6:
            return "Incomplete registration. Please provide all required details.", 400
        
        name, age, gender, county, town, contact_number= registration_data[:6]
        
        # Register the user with default contact number
        register_user(name, int(age), gender, county, town, contact_number)
        
        # Prompt user to add additional details
        response_message = "Your profile has been created successfully.\n"
        response_message += "Would you like to add additional details? Reply with 'Yes' or 'No'."
        
        return response_message

    if sms_text.lower() == "yes":
        # User wants to add additional details
        response_message = "SMS details#levelOfEducation#profession#maritalStatus#religion#ethnicity to 22141.\n"
        response_message += "E.g. details#diploma#driver#single#christian#mijikenda"
        return response_message

    if sms_text.lower() == "no":
        # User doesn't want to add additional details
        return "You are now registered for dating\nTo search for a MPENZI, SMS match#age#town to 22141 and meet the person of your dreams"

    if sms_text.startswith("details"):
        additional_details = sms_text.split("#")[1:]
        if len(additional_details) != 5:
            return "Invalid command. Please provide all required additional details.", 400
            
        user = session.query(User).order_by(User.id.desc()).first()  # Get the last registered user
        if user:
            user.level_of_education = additional_details[0]
            user.profession = additional_details[1]
            user.marital_status = additional_details[2]
            user.religion = additional_details[3]
            user.ethnicity = additional_details[4]
            session.commit()
            return "This is the last stage of registration\nSMS a brief description of yourself to 22141 starting with the word MYSELF E.g., MYSELF chocolate, lovely, sexy etc"
        else:
            return "No user found. Please register first.", 400

    if sms_text.startswith("MYSELF"):
        description = sms_text.split("MYSELF", 1)[-1].strip()
        # Process and save self-description
        process_self_description(description)
        return "You are now registered for dating\nTo search for a MPENZI, SMS match#age#town to 22141 and meet the person of your dreams"

    return "Invalid command. Please follow the registration instructions."

if __name__ == '__main__':
    app.run(debug=True)
