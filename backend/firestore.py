# firestore.py

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def initialize_firestore():
    cred = credentials.Certificate('secret/eduaisystem-firebase-adminsdk-f8s0n-187930ae20.json')
    firebase_admin.initialize_app(cred)
    return firestore.client()
