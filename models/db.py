from pymongo import MongoClient
import os

client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"))
db = client.get_default_database()
db_name = os.getenv("DB_NAME", "nova")
db = client[db_name]

users_collection = db['users']
contacts_collection = db['contacts']
chat_history_collection = db['chats']
otp_collection = db['otp_verifications']
