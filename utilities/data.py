import nltk, sqlite3
from nltk.corpus import words
from firebase_admin import firestore, initialize_app, credentials

nltk.download('words')
conn = sqlite3.connect("dict_hh.db")
cursor = conn.cursor()

cred = credentials.Certificate('credentials.json')
initialize_app(cred)
db = firestore.client()

def get_user_data(user_id):
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    if not user.exists:
        user_ref.set({
            'vocab': {}
        })
        user = user_ref.get()
    return user_ref, user.to_dict()

def update_user_data(user_id, data):
    user_ref, _ = get_user_data(user_id)
    user_ref.update(data)

def is_valid_word(word):
    return word.lower() in words.words()