import pymongo
from pyrogram import Client, filters

# Initialize the MongoDB client
mongo_client = pymongo.MongoClient("mongodb+srv://rishu:rishu@cluster0.gzidqw6.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client["telegram_bot_db"]
collection = db["messages"]

# Initialize the Pyrogram client
api_id = 14091414
api_hash = "1e26ebacf23466ed6144d29496aa5d5b"
bot_token = "6120849671:AAEx6gtXx34Ak-X1EaAkgdUkWq6YgvfqjAk"

app = Client("telegram_bot", api_id, api_hash, bot_token=bot_token)


def save_message_to_db(client, message):
    if message.text.startswith("#"):
        collection.insert_one({"message": message.text})


def authorize_user(user_id):
    authorized_users = [5500572462]  # Add the authorized user IDs here
    return user_id in authorized_users


@app.on_message(filters.group)
def handle_group_message(client, message):
    save_message_to_db(client, message)


@app.on_message(filters.command("r"))
def handle_r_command(client, message):
    if message.chat.type == "private" or authorize_user(message.from_user.id):
        messages = collection.find({}, {"_id": 0, "message": 1})
        response = "\n".join([f"{i+1}. {doc['message']}" for i, doc in enumerate(messages)])
        client.send_message(message.chat.id, response)


@app.on_message(filters.command("del"))
def handle_del_command(client, message):
    if message.chat.type == "private" or authorize_user(message.from_user.id):
        command_parts = message.text.split(" ")
        if len(command_parts) > 1:
            del_message = " ".join(command_parts[1:])
            collection.delete_one({"message": {"$regex": f"^{del_message}$", "$options": "i"}})
            client.send_message(message.chat.id, f"Deleted message: {del_message}")


app.run()
