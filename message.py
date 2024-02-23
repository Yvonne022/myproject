from flask import Blueprint, app, jsonify, request
from model import Message, User, Session

message_blueprint = Blueprint('message', __name__)


@message_blueprint.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    sender_id = data['sender_id']
    recipient_id = data['recipient_id']
    body = data['body']

    
    sender = User.query.get(sender_id)
    if not sender:
        return "Invalid sender", 400

    
    recipient = User.query.get(recipient_id)
    if not recipient:
        return "Invalid recipient", 400

    # Create and add message
    message = Message(
        from_user_id=sender_id,
        to_user_id=recipient_id,
        body=body
    )

    # Use the Flask application's session instead of Session directly
    app.session.add(message)
    app.session.commit()

    return "Message sent!", 201


@message_blueprint.route('/messages/<int:user_id>')
def get_messages(user_id):
    # Query messages for the specified user ID
    messages = Message.query.filter_by(to_user_id=user_id).all()

    if not messages:
        return "No messages found for this user", 404

    # Return messages as JSON
    return jsonify([{
        "id": message.id,
        "from_user_id": message.from_user_id,
        "to_user_id": message.to_user_id,
        "body": message.body,
        # Add other fields as needed
    } for message in messages])
