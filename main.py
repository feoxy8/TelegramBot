from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = '7324851083:AAEOWTNYBsFG2ZrVNEakCuXG-xRDwaQH6Wg'
BOT_USERNAME: Final = '@iSplitMoneyBot'

# Command handler for /start or /test command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks for chatting with me!')

# Generic handler for unrecognized input
async def handle_unrecognized_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't recognize that command. Please try again or type /help for available commands.")

# Error handler (logs and replies to the user in case of errors)
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Log the error
    print(f"Error: {context.error}")

    # Check if the update has a message or callback query
    if update and update.message:
        await update.message.reply_text('An error occurred. Please try again later.')
    elif update and update.callback_query:
        await update.callback_query.answer('An error occurred. Please try again later.')
    else:
        print("Update type not handled by error handler")

if __name__ == '__main__':
    # Create the application instance
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler('test', start_command))
    
    # Generic handler for all unrecognized messages or commands
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unrecognized_input))

    # Error handler to catch any issues
    app.add_error_handler(error_handler)

    # Start the bot
    app.run_polling(poll_interval=1)
