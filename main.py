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

# Add authorized users to Sudo list
Sudo = [123456789, 987654321]  # Replace with your authorized user IDs

# Save messages starting with "#" to the MongoDB collection
@app.on_message(filters.text & filters.group)
def save_message(client, message):
    if message.text.startswith("#"):
        collection.insert_one({"message_id": message.message_id, "text": message.text})

# Show the list of saved messages
@app.on_message(filters.command(["r"], prefixes="/") & filters.user(Sudo))
def show_list(client, message):
    cursor = collection.find()
    count = collection.count_documents({})
    response = "List of saved messages:\n"
    for index, doc in enumerate(cursor, start=1):
        response += f"{index}. {doc['text']}\n"
    response += f"Total messages: {count}"
    message.reply_text(response)

# Delete a specific message from the MongoDB collection
@app.on_message(filters.command(["del"], prefixes="/") & filters.user(Sudo))
def delete_message(client, message):
    text = message.text[5:].strip().lower()
    deleted_count = collection.delete_many({"text": {"$regex": f"^{text}$", "$options": "i"}}).deleted_count
    message.reply_text(f"Deleted {deleted_count} message(s) with text '{text}'")

# Start the bot
app.run()
