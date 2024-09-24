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
ASK_NAMES, ASK_MENU_ITEM, ASK_PRICE, ASK_PAYER = range(4)

# Data storage
users = []
menu_data = []

# Start command handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received update: {update}")  # Log update data
    await update.message.reply_text('Hello! Please enter names separated by hyphen(-).')
    return ASK_NAMES  # Move to the state where bot expects user to input names

# Handler to capture user's names
async def input_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Entered input_user handler")  # Log to ensure this handler is reached
    
    global users
    users = update.message.text.split('-')  # Split the names by '-'
    users = [name.strip() for name in users]  # Remove any extra whitespace around each name
    num = len(users)
    logger.info(f"Received names: {users}, Number of people: {num}")
    
    if num > 1:
        name_list = "\n".join(users)  # Format the names nicely for display
        await update.message.reply_text(f'Nice to meet all of you:\n{name_list}')
    else:
        await update.message.reply_text(f'Nice to meet you, {users[0]}!')
    
    await update.message.reply_text("Let's start adding menu items. Please enter the menu in the format: 'Item, Price, Payer; Item2, Price2, Payer2; ...'.")
    return ASK_MENU_ITEM  # Move to next state to ask for menu input

# Handler to capture menu items, prices, and payers in one message
async def input_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global menu_data
    global users
    
    # Split the input by semicolons to get each menu item entry
    entries = update.message.text.split(';')
    
    for entry in entries:
        # Split each entry by commas to get item, price, and payer
        try:
            item, price, payer = [part.strip() for part in entry.split(',')]
        except ValueError:
            await update.message.reply_text(f'Invalid format for entry: {entry}. Please use the format "Item, Price, Payer".')
            return ASK_MENU_ITEM
        
        # Check if price is a valid number
        if not price.replace('.', '', 1).isdigit():
            await update.message.reply_text(f'Invalid price for entry: {entry}. Please enter a valid number for the price.')
            return ASK_MENU_ITEM
        
        price = float(price)  # Convert price to a floating-point number
        
        # Check if the payer is valid
        if payer.lower() == 'all':
            payer = 'all'
        elif payer not in users:
            await update.message.reply_text(f'Payer "{payer}" not recognized. Please enter a valid name or "all".')
            return ASK_MENU_ITEM
        
        # Store the current menu item, price, and payer
        menu_item = {
            'item': item,
            'price': price,
            'payer': payer
        }
        menu_data.append(menu_item)
    
    # Display the added menu data
    item_summary = '\n'.join([f'{item["item"]} - {item["price"]} (Payer: {item["payer"]})' for item in menu_data])
    await update.message.reply_text(f'Menu items added:\n{item_summary}')
    
    # Ask if they want to finish or add more
    await update.message.reply_text('If you\'re done, type /done to finish and see the summary. If you want to add more items, send them in the same format.')
    return ASK_MENU_ITEM  # Allow them to add more items if they want

# End the conversation when the user is done adding items
async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payer_totals = {}

    # Loop through each item in the menu_data
    for item in menu_data:
        payer = item["payer"]
        price = item["price"]

        if payer == "all":
            # Split the price among all users
            split_price = price / len(users)
            for user in users:
                if user in payer_totals:
                    payer_totals[user] += split_price
                else:
                    payer_totals[user] = split_price
        else:
            # Add the price to the corresponding payer's total
            if payer in payer_totals:
                payer_totals[payer] += price
            else:
                payer_totals[payer] = price

    # Create the summary for each item
    item_summary = '\n'.join([f'{item["item"]} - {item["price"]} (Payer: {item["payer"]})' for item in menu_data])

    # Create the summary of how much each payer owes
    total_summary = '\n'.join([f'{payer} owes: {total:.2f}' for payer, total in payer_totals.items()])

    # Send the final summary to the user
    await update.message.reply_text(
        f"Here's the final summary:\n{item_summary}\n\nTotal per payer:\n{total_summary}"
    )

    return ConversationHandler.END  # End the conversation

# Fallback handler for cancellation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Conversation canceled.")
    await update.message.reply_text('Conversation canceled.')
    return ConversationHandler.END  # End the conversation

# Help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Log the help command usage
    logger.info("/help command was called")

    # Prepare help message to send to the user
    help_message = (
        "/cancel - Cancel the current calculation\n"
        "/done - Finish and get the summary of the calculation\n"
        "/help - Ask for command list"
    )
    
    # Send help message to the user
    await update.message.reply_text(help_message)

    return ConversationHandler.END

if __name__ == '__main__':
    # Create the application
    app = Application.builder().token(TOKEN).build()

    # Define conversation handler with states
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],  # Start with /start command
        states={
            ASK_NAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_user)],  # Expect user names
            ASK_MENU_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_menu)],  # Expect full menu input
        },
        fallbacks=[CommandHandler('cancel', cancel), 
                   CommandHandler('done', end_conversation)]  # Allow canceling or finishing
    )

    # Add the /help command handler
    app.add_handler(CommandHandler('help', help))

    # Add conversation handler to the app
    app.add_handler(conversation_handler)

    # Start the bot
    app.run_polling(poll_interval=1)
