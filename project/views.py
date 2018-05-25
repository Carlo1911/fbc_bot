import os
import requests
import random
import json
from datetime import datetime, date
from flask import Flask, request, Blueprint

from project import db, bot
from project.models import User, Song


project_blueprint = Blueprint(
    'home', __name__,
)


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
                print(message['postback'].get('title'))
                if 'Agregar canción' == message['postback'].get('title'):
                    track_id = message['postback'].get('payload')
                    add_music(recipient_id, track_id)
                    send_message(recipient_id, 'Canción agregada')
                if 'Lista de favoritos' == message['postback'].get('title'):
                    favorite_songs = get_favorite_songs(recipient_id)
                    print(favorite_songs)
                    send_message(recipient_id, favorite_songs)
                if 'Mostrar usuarios' == message['postback'].get('title'):
                    total_users = get_total_users()
                    send_message(recipient_id, total_users)
                if 'Chats hoy' == message['postback'].get('title'):
                    chats_today = get_total_chats()
                    send_message(recipient_id, chats_today)
            if message.get('message'):
                recipient_id = message['sender']['id']
                mensaje = message['message'].get('text')
                if message['message'].get('text'):
                    if 'buscar:' in mensaje:
                        results = get_results(
                            mensaje.split('buscar:')[1].strip())
                        send_generic_message(recipient_id, results[:3])
                    if 'Reportes:' in mensaje:
                        reports = get_reports()
                        send_generic_message(recipient_id, reports)
    return "Message Processed"


def add_music(recipient_id, track_id):
    user_info = bot.get_user_info(recipient_id)
    user = User.query.filter_by(recipient_id=recipient_id).first()
    # check if user exists in bd
    if not user:
        user = User(
            recipient_id=recipient_id,
            first_name=user_info['first_name'],
            last_name=user_info['last_name'])
        db.session.add(user)
    else:
        # Update user's last conection
        user.last_connection = datetime.utcnow()
    db.session.commit()
    parameters = {
        'apikey': '2df63ad0b5eb5f9d024490851cb059a7',
        'track_id': track_id,
    }
    api_url = 'http://api.musixmatch.com/ws/1.1/track.get'
    response = requests.get(api_url, params=parameters)
    results = None
    if response.status_code == 200:
        results = json.loads(response.content.decode('utf-8'))
        track = results['message']['body']['track']
        song = Song.query.filter_by(track_id=track_id).first()
        # check if song exist in bd
        if not song:
            song = Song(track_id=track_id,
                        track_name=track['track_name'],
                        artist_name=track['artist_name'])
            db.session.add(song)
        favorite_song = User.query.filter(
            User.songs_list.any(track_id=track_id)).first()
        # check if user has song as favorite
        if favorite_song:
            favorite_song.searched_times += 1
        else:
            user.songs_list.append(song)
        db.session.commit()


def get_total_chats():
    start = date.today()
    total_chats = User.query.filter(User.last_connection >= start).count()
    return 'Total chats de hoy: {}'.format(total_chats)


def get_total_users():
    total_users = User.query.count()
    return 'Total de usuarios: {}'.format(total_users)


def get_favorite_songs(recipient_id):
    user = User.query.filter_by(recipient_id=recipient_id).first()
    favorite_songs = ''
    for song in user.songs_list:
        favorite_songs += '{} - {}\n'.format(song.track_name, song.artist_name)
    return favorite_songs


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


def get_reports():
    reports = [
        {
            "title": 'Canciones favoritas',
            "buttons": [{
                "type": "postback",
                "title": "Lista de favoritos",
                "payload": "True",
            }],
        },
        {
            "title": 'Total de usuarios',
            "buttons": [{
                "type": "postback",
                "title": "Mostrar usuarios",
                "payload": "True",
            }],
        },
        {
            "title": 'Chats de hoy',
            "buttons": [{
                "type": "postback",
                "title": "Chats hoy",
                "payload": "True",
            }]
        }
    ]
    return reports


def send_generic_message(recipient_id, elements):
    bot.send_generic_message(recipient_id, elements)


def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)
