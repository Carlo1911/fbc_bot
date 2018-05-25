from project import db
from datetime import datetime


favorites = db.Table('favorites',
                     db.Column('users_recipient_id', db.String(18),
                               db.ForeignKey('users.recipient_id')),
                     db.Column('songs_track_id', db.String(18),
                               db.ForeignKey('songs.track_id')),
                     db.UniqueConstraint(
                         'users_recipient_id', 'songs_track_id',
                         name='UC_user_id_song_id')
                     )


class User(db.Model):
    __tablename__ = 'users'
    recipient_id = db.Column(db.String(18), primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_connection = db.Column(
        db.DateTime, default=datetime.utcnow)
    songs_list = db.relationship(
        'Song',
        secondary=favorites,
        backref=db.backref('songs_list', lazy='dynamic')
    )

    def __init__(self, recipient_id, first_name, last_name):
        self.recipient_id = recipient_id
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return '<User %r>' % (self.recipient_id)


class Song(db.Model):
    __tablename__ = 'songs'
    track_id = db.Column(db.String(18), primary_key=True)
    track_name = db.Column(db.String(120))
    artist_name = db.Column(db.String(120))
    searched_times = db.Column(db.Integer)
    users_list = db.relationship(
        'User',
        secondary=favorites,
        backref=db.backref('users_list', lazy='dynamic'))

    def __init__(self, track_id, track_name, artist_name):
        self.track_id = track_id
        self.track_name = track_name
        self.artist_name = artist_name
        self.searched_times = 1

    def __repr__(self):
        return '<Song %r>' % (self.track_name)
