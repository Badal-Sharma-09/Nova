from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from datetime import datetime
from models.db import chat_history_collection
from utils.gemini_bot import get_gemini_response, get_gemini_model

chat_bp = Blueprint("chat", __name__)


@chat_bp.route('/chat', methods=['POST'])
def chat():
    print("[CHAT] Payload:", request.json)
    print("[CHAT] session.username:", session.get("username"))

    if not session.get('username'):
        return jsonify({"error": "Please login to chat"}), 401

    user_input = request.json.get("message")
    chat_id = request.json.get("chat_id")

    if not user_input or user_input.strip() == "":
        return jsonify({"error": "Message is required"}), 400

    try:
        chat = None
        if chat_id:
            chat = chat_history_collection.find_one({
                "_id": ObjectId(chat_id),
                "username": session.get('username')
            })

        if not chat:
            chat = {
                "username": session.get('username'),
                "timestamp": datetime.utcnow(),
                "history": [],
                "title": "New Chat"
            }
            result = chat_history_collection.insert_one(chat)
            chat_id = str(result.inserted_id)

        history = chat.get('history', [])

        try:
            response_text = get_gemini_response(user_input, history)
        except Exception as e:
            if "API Limit Exceeded" in str(e) or "quota" in str(e).lower():
                return jsonify({"error": "API Limit Exceeded"}), 429
            return jsonify({"error": str(e)}), 500

        new_history = history + [
            {"role": "user", "parts": [user_input]},
            {"role": "model", "parts": [response_text]}
        ]

        update_fields = {
            "history": new_history,
            "timestamp": datetime.utcnow()
        }

        if len(history) == 0:
            update_fields["title"] = user_input[:50] + "..." if len(user_input) > 50 else user_input

        chat_history_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": update_fields}
        )

        return jsonify({
            "response": response_text,
            "chat_id": str(chat_id)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    if not session.get('username'):
        return jsonify({"error": "Not logged in"}), 401

    try:
        chat_sessions = list(chat_history_collection.find(
            {"username": session.get('username')},
            {"_id": 1, "timestamp": 1, "title": 1}
        ).sort("timestamp", -1))

        for chat in chat_sessions:
            chat['_id'] = str(chat['_id'])
            chat['timestamp'] = chat.get('timestamp', datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")
            if 'title' not in chat:
                chat['title'] = "Chat " + chat['timestamp']

        return jsonify({"chats": chat_sessions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/get_chat_messages/<chat_id>', methods=['GET'])
def get_chat_messages(chat_id):
    if not session.get('username'):
        return jsonify({"error": "Not logged in"}), 401

    try:
        chat = chat_history_collection.find_one({
            "_id": ObjectId(chat_id),
            "username": session.get('username')
        })

        if not chat:
            return jsonify({"error": "Chat not found"}), 404

        return jsonify({
            "history": chat.get('history', []),
            "title": chat.get('title', "Chat " + chat['timestamp'].strftime("%Y-%m-%d %H:%M:%S"))
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/create_chat', methods=['POST'])
def create_chat():
    if not session.get('username'):
        return jsonify({"error": "Not logged in"}), 401

    try:
        model = get_gemini_model()
        if model is None:
            return jsonify({"error": "API Limit Exceeded"}), 429

        chat = {
            "username": session.get('username'),
            "timestamp": datetime.utcnow(),
            "history": [],
            "title": "New Chat"
        }
        result = chat_history_collection.insert_one(chat)

        return jsonify({
            "chat_id": str(result.inserted_id),
            "timestamp": chat['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
            "title": chat['title']
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/delete_chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    if not session.get('username'):
        return jsonify({"error": "Not logged in"}), 401

    try:
        result = chat_history_collection.delete_one({
            "_id": ObjectId(chat_id),
            "username": session.get('username')
        })

        if result.deleted_count == 0:
            return jsonify({"error": "Chat not found"}), 404

        return jsonify({"message": "Chat deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/update_chat_title/<chat_id>', methods=['PUT'])
def update_chat_title(chat_id):
    if not session.get('username'):
        return jsonify({"error": "Not logged in"}), 401

    try:
        title = request.json.get('title')
        if not title:
            return jsonify({"error": "Title is required"}), 400

        result = chat_history_collection.update_one(
            {
                "_id": ObjectId(chat_id),
                "username": session.get('username')
            },
            {"$set": {"title": title}}
        )

        if result.modified_count == 0:
            return jsonify({"error": "Chat not found"}), 404

        return jsonify({"message": "Title updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
