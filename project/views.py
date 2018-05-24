import os
import requests
import random
import json
from flask import Flask, request, Blueprint

from project import db, bot
from project.models import User


project_blueprint = Blueprint(
    'home', __name__,
)   # pragma: no cover


@project_blueprint.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Ok", 200


@project_blueprint.route('/', methods=['POST'])
def webhook():

    output = request.get_json()
    print(output)
    for event in output['entry']:
        messaging = event['messaging']
        for message in messaging:
            if message.get('postback'):
                recipient_id = message['sender']['id']
                track_id = message['postback'].get('payload')
                add_music(recipient_id, track_id)
                # add_music(recipient_id, track_id)
            if message.get('message'):
                recipient_id = message['sender']['id']
                mensaje = message['message'].get('text')
                if message['message'].get('text'):
                    if mensaje == 'Hola':
                        send_message(recipient_id, 'Hola')
                        print(bot.get_user_info(recipient_id))
                    else:
                        if 'buscar:' in mensaje:
                            results = get_results(
                                mensaje.split('buscar:')[1].strip())
                        response_sent_text = get_message()
                        send_message(recipient_id, response_sent_text)
                        send_generic_message(recipient_id, results[:3])
                # if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def add_music(recipient_id, track_id):
    user_info = bot.get_user_info(recipient_id)
    user = User.query.filter_by(recipient_id=recipient_id).first()
    if user:
        # agregar música
        pass
    else:
        user = User(
            recipient_id=recipient_id,
            first_name=user_info['first_name'],
            last_name=user_info['last_name'])
        db.session.add(user)
        db.session.commit()
    return "success"


def get_results(searched_word):
    parameters = {
        'apikey': '2df63ad0b5eb5f9d024490851cb059a7',
        'q_track': searched_word,
    }
    api_url = 'http://api.musixmatch.com/ws/1.1/track.search'
    response = requests.get(api_url, params=parameters)

    results = None
    if response.status_code == 200:
        results = json.loads(response.content.decode('utf-8'))
        track_list = results['message']['body']['track_list']
        print("Canción - Artista")
        songs = []
        for element in track_list:
            song_info = {
                "title": element['track']['track_name'],
                "subtitle": element['track']['artist_name'],
                "buttons": [{
                    "type": "postback",
                    "title": "Agregar canción",
                    "payload": str(element['track']['track_id']),
                }],
            }
            songs.append(song_info)
        results = songs
    return results


def send_generic_message(recipient_id, elements):
    bot.send_generic_message(recipient_id, elements)
    return "success"


def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.",
                        "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)


def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


def send_button_message(recipient_id, response):
    buttons = [
        {
            "type": "web_url",
            "url": "https://www.messenger.com",
            "title": "Visit Messenger"
        },
        {
            "type": "postback",
            "title": "Agregar canción: One kiss",
            "payload": "track_id: 12313131321"
        }
    ]
    bot.send_button_message(recipient_id, response, buttons)
    return "success"