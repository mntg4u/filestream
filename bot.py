import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import BOT_TOKEN, CHANNEL_ID, LOGS_CHANNEL_ID
from urllib.parse import quote

# Check if the user is a subscriber
def check_subscription(user_id, context: CallbackContext):
    chat_member = context.bot.get_chat_member(CHANNEL_ID, user_id)
    return chat_member.status in ["member", "administrator", "creator"]

# Start command
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not check_subscription(user_id, context):
        keyboard = [
            [InlineKeyboardButton("Subscribe to the Channel", url=f"https://t.me/{CHANNEL_ID[1:]}")]
        ]
        update.message.reply_text(
            "You must subscribe to our channel to use this bot.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    update.message.reply_text("Welcome! Send me a file, and I'll provide a direct download/stream link.")

# Handle file messages
def handle_file(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not check_subscription(user_id, context):
        keyboard = [
            [InlineKeyboardButton("Subscribe to the Channel", url=f"https://t.me/{CHANNEL_ID[1:]}")]
        ]
        update.message.reply_text(
            "You must subscribe to our channel to use this bot.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    file = update.message.document or update.message.video or update.message.photo[-1]
    file_id = file.file_id
    file_name = file.file_name if hasattr(file, "file_name") else "file"

    # Log file details to logs channel
    context.bot.send_message(
        LOGS_CHANNEL_ID,
        f"User {user_id} sent a file:\nName: {file_name}\nFile ID: {file_id}",
    )

    # Generate a file link
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_id}"
    download_link = f"https://your-host.com/download/{quote(file_name)}"

    # Respond to the user
    update.message.reply_text(
        f"File received: {file_name}\n\n[Download Link]({download_link})\n[Stream Link]({file_url})",
        parse_mode="Markdown",
    )

# Error handler
def error_handler(update: Update, context: CallbackContext):
    context.bot.send_message(LOGS_CHANNEL_ID, f"Error: {context.error}")

# Main function
def main():
    updater = Updater(BOT_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document | Filters.video | Filters.photo, handle_file))
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
