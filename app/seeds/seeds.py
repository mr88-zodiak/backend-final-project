from app.extends import db
from app.models.user import Register_login

def seed_data():
    users_to_seed = [
        {"name": "cohen", "email": "cohen@mail.com", 'username': "cohen", "password": "aku123", "role": "donatur"},
        {"name": "budi", "email": "budi@mail.com", 'username': "budi", "password": "aku123", "role": "donatur"},
        {"name": "sari", "email": "sari@mail.com", 'username': "sari", "password": "aku123", "role": "donatur"},
        {"name": "yohanes", "email": "donatur1@mail.com", 'username': "donatur1", "password": "aku123", "role": "donatur"},
        {"name": "peter", "email": "donatur2@mail.com", 'username': "donatur2", "password": "aku123", "role": "donatur"},
        {'name': "mark", "email": "donatur3@mail.com", 'username': "donatur3", "password": "aku123", "role": "donatur"},
        {'name': "joseph", "email": "donatur4@mail.com", 'username': "donatur4", "password": "aku123", "role": "donatur"},
        {'name': "maria", "email": "donatur5@mail.com", 'username': "donatur5", "password": "aku123", "role": "donatur"},
        {'name': "anastasia", "email": "donatur6@mail.com", 'username': "donatur6", "password": "aku123", "role": "donatur"},
        {'name': "susan", "email": "donatur7@mail.com", 'username': "donatur7", "password": "aku123", "role": "donatur"},
        {'name': "putri", "email": "donatur8@mail.com", 'username': "donatur8", "password": "aku123", "role": "donatur"},
    ]
    for user_data in users_to_seed:
        user = Register_login(**user_data)
        db.session.add(user)