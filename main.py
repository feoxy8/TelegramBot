from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from manual_input import handle_manual_input, handle_done  # Ensure these functions are defined in manual_input.py

TOKEN = '7324851083:AAEOWTNYBsFG2ZrVNEakCuXG-xRDwaQH6Wg'

# Define the states
ASK_NAMES = 1  # For name input
MANUAL_INPUT = 2  # For manual menu input

# Start command handler
async def start_command(update, context):
    await update.message.reply_text('Hello! Please enter names separated by hyphen(-).')
    context.user_data['menu_data'] = []  # Initialize menu data if needed later
    return ASK_NAMES  # Move to the state where the bot waits for input (names)

# Handler to process names input
async def handle_names(update, context):
    # Split names by hyphen and clean up spaces
    users = update.message.text.split('-')
    users = [user.strip() for user in users if user.strip()]

    if len(users) == 0:
        await update.message.reply_text('Please enter at least one name.')
        return ASK_NAMES

    # Log and store the users
    context.user_data['users'] = users
    num_of_people = len(users)
    
    # Display names
    formatted_names = "\n".join(users)
    await update.message.reply_text(f"Nice to meet all of you:\n{formatted_names}")
    await update.message.reply_text(f"Number of people: {num_of_people}")

    # Now ask for the menu input
    await update.message.reply_text("Now you can start entering menu items in the format: 'Item, Price, Payer1, Payer2'.")
    return MANUAL_INPUT  # Transition to manual input

# Main function to initialize the bot
def main():
    app = Application.builder().token(TOKEN).build()

    # Conversation handler for name input and manual input
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],  # Start conversation
        states={
            ASK_NAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_names)],  # Handles names
            MANUAL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_input)],  # Handles menu input
        },
        fallbacks=[CommandHandler('done', handle_done)],  # End the conversation with /done
    )

    # Add the conversation handler to the bot
    app.add_handler(conv_handler)

    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()
