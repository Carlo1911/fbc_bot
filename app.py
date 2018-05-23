# -*- coding: utf-8 -*-
"""application instance."""
import os
import random
from datetime import datetime
import requests
from pymessenger.bot import Bot
from flask import Flask, request

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/fbc_db'
bot = Bot(os.environ["PAGE_ACCESS_TOKEN"])


@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Ok", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    output = request.get_json()
    print(output)
    for event in output['entry']:
        messaging = event['messaging']
        for message in messaging:
            if message.get('message'):
                # Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                mensaje = message['message'].get('text')
                if message['message'].get('text'):
                    print(mensaje)
                    if mensaje == 'Hola':
                        send_message(recipient_id, 'Hola')
                    else:
                        response_sent_text = get_message()
                        send_message(recipient_id, response_sent_text)
                # if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"

# chooses a random message to send to the user


def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.",
                        "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

# uses PyMessenger to send response to user


def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == '__main__':
    app.run(port=5000, debug=True)
