from project import db


class User(db.Model):
    __tablename__ = 'fb_users'
    recipient_id = db.Column(db.String(18), primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(120))

    def __init__(self, recipient_id, first_name, last_name):
        self.recipient_id = recipient_id
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return '<User %r>' % (self.recipient_id)
