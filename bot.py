import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pymongo import MongoClient
from bson.json_util import dumps  # Import dumps to convert MongoDB data to JSON

# MongoDB connection setup
client = MongoClient('Mongodb_URI')  # Connect to your MongoDB instance
db = client['mydatabase']  # Use your database name
collection = db['userdata']  # Use your collection name

# Enable logging to track errors and information in logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Start command that will be triggered by '/start'
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    update.message.reply_text(f'Hello {user.first_name}, welcome to the bot! You can store data with /store, retrieve data with /get_data, or check usage with /usage.')

# Function to handle storing data into MongoDB
def store_data(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    message_text = ' '.join(context.args)  # Get message text from the command arguments
    
    if not message_text:
        update.message.reply_text("Please provide data to store after the /store command.")
        return

    # Create user data object to store
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'message': message_text,
        'chat_id': update.message.chat_id
    }
    
    # Insert the data into the MongoDB collection
    collection.insert_one(user_data)
    
    # Send confirmation to the user
    update.message.reply_text(f'Thank you, {user.first_name}! Your message "{message_text}" has been saved.')

# Function to handle downloading data from MongoDB
def get_data(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_data = collection.find_one({'user_id': user.id})  # Find data for the current user by their user_id
    
    if user_data:
        # Format the result in JSON format and send as message
        user_data_json = dumps(user_data, indent=4)  # Convert to a readable JSON format
        update.message.reply_text(f'Here is your stored data:\n{user_data_json}')
    else:
        update.message.reply_text("No data found for you.")

# Function to get MongoDB database usage statistics
def usage(update: Update, context: CallbackContext) -> None:
    # Fetch database stats (storage information)
    stats = db.command("dbStats")  # dbStats provides information about storage
    storage_info = f"Database Usage Info:\n\n"
    storage_info += f"Data Size: {stats['dataSize']} bytes\n"
    storage_info += f"Storage Size: {stats['storageSize']} bytes\n"
    storage_info += f"Total Index Size: {stats['indexSize']} bytes\n"
    storage_info += f"Document Count: {stats['objects']}\n"
    storage_info += f"Collection Count: {stats['collections']}\n"
    storage_info += f"Avg. Object Size: {stats['avgObjSize']} bytes"
    
    # Send the database usage info to the user
    update.message.reply_text(storage_info)

# Function to log errors
def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Main function to set up the Telegram bot
def main() -> None:
    # Telegram bot token (replace with your actual token)
    token = 'your_bot_token'

    # Set up the Updater and dispatcher
    updater = Updater(token)

    # Add handlers for various commands and messages
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))  # /start command
    dispatcher.add_handler(CommandHandler('store', store_data))  # /store command
    dispatcher.add_handler(CommandHandler('get_data', get_data))  # /get_data command
    dispatcher.add_handler(CommandHandler('usage', usage))  # /usage command to show database stats

    # Handle any errors that might occur
    dispatcher.add_error_handler(error)

    # Start polling for updates
    updater.start_polling()

    # Keep the bot running until manually stopped
    updater.idle()

if __name__ == '__main__':
    main()

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Accessing the environment variables
token = os.getenv('TELEGRAM_BOT_TOKEN')
mongo_uri = os.getenv('MONGO_URI')
