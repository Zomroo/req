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


@app.on_message(filters.group & filters.text)
def save_message(client, message):
    # Check if the message starts with #
    if message.text.startswith("#"):
        # Save the message to the MongoDB collection
        collection.insert_one({"message": message.text, "chat_id": message.chat.id, "user_id": message.from_user.id})


@app.on_message(filters.group & filters.command("r") & filters.user("user_id"))
def show_messages(client, message):
    # Fetch all the messages from the MongoDB collection
    messages = collection.find({"chat_id": message.chat.id})
    
    response = ""
    count = 1
    for msg in messages:
        response += f"{count}. {msg['message']}\n"
        count += 1
    
    # Send the response to the group
    client.send_message(message.chat.id, response)


@app.on_message(filters.group & filters.command("del") & filters.user("user_id"))
def delete_message(client, message):
    # Get the text after the /del command
    query = message.text.split(maxsplit=1)[1].lower()

    # Search for the message in the MongoDB collection
    result = collection.find_one({"chat_id": message.chat.id, "message": {"$regex": query, "$options": "i"}})
    
    if result:
        # Delete the message from the MongoDB collection
        collection.delete_one({"_id": result["_id"]})
        response = "Message deleted successfully."
    else:
        response = "Message not found."
    
    # Send the response to the group
    client.send_message(message.chat.id, response)


app.run()
