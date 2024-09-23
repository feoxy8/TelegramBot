import logging
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN: Final = '7324851083:AAEOWTNYBsFG2ZrVNEakCuXG-xRDwaQH6Wg'
BOT_USERNAME: Final = '@iSplitMoneyBot'

# Define states for conversation
ASK_NAMES = 1

# Start command handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received update: {update}")  # Log update data
    await update.message.reply_text('Hello! Please enter participant names separated by a hyphen (-).')
    return ASK_NAMES  # Move to the state where bot expects user to input names

# Handler to capture user's names
async def input_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    names = update.message.text.split('-')  # Split the names by '-'
    names = [name.strip() for name in names]  # Remove any extra whitespace around each name
    logger.info(f"Received names: {names}")
    
    if len(names) > 1:
        name_list = "\n".join(names)  # Format the names nicely for display
        await update.message.reply_text(f'Nice to meet all of you:\n{name_list}')
    else:
        await update.message.reply_text(f'Nice to meet you, {names[0]}!')
    
    return ConversationHandler.END  # End the conversation after receiving the names

# Fallback handler if user cancels the process
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Conversation canceled.')
    return ConversationHandler.END

if __name__ == '__main__':
    # Create the application
    app = Application.builder().token(TOKEN).build()

    # Define conversation handler with states
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],  # Start with /start command
        states={
            ASK_NAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_user)],  # Expect multiple names as text
        },
        fallbacks=[CommandHandler('cancel', cancel)],  # Allow canceling the conversation
    )

    # Add conversation handler to the app
    app.add_handler(conversation_handler)

    # Start the bot
    app.run_polling()
