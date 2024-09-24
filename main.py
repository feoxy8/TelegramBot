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
ASK_NAMES, ASK_MENU_ITEM = range(2)

# Data storage
users = []
menu_data = []

# Start command handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received update: {update}")
    await update.message.reply_text('Hello! Please enter names separated by hyphen(-).')
    return ASK_NAMES  # Move to the state where bot expects user to input names

# Handler to capture user's names
async def input_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users
    users = update.message.text.split('-')
    users = [name.strip() for name in users]  # Remove any extra whitespace around each name
    num = len(users)
    logger.info(f"Received names: {users}, Number of people: {num}")
    
    if num > 1:
        name_list = "\n".join(users)
        await update.message.reply_text(f'Nice to meet all of you:\n{name_list}')
    else:
        await update.message.reply_text(f'Nice to meet you, {users[0]}!')
    
    await update.message.reply_text("Let's start adding menu items. Please enter the menu in the format: 'Item, Price, Payer1, Payer2;...'. Payers can be multiple, separated by commas.")
    return ASK_MENU_ITEM  # Move to next state to ask for menu input

# Handler to capture menu items, prices, and payers
async def input_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global menu_data
    global users
    
    entries = update.message.text.split(';')
    
    for entry in entries:
        # Split entry by commas, taking the first part as the item, the second part as the price,
        # and the rest as the list of payers
        parts = [part.strip() for part in entry.split(',')]
        
        if len(parts) < 3:
            await update.message.reply_text(f'Invalid format for entry: {entry}. Please use the format "Item, Price, Payers".')
            return ASK_MENU_ITEM
        
        item = parts[0]  # The first part is the menu item
        price = parts[1]  # The second part is the price
        
        # Validate price
        if not price.replace('.', '', 1).isdigit():
            await update.message.reply_text(f'Invalid price for entry: {entry}. Please enter a valid number for the price.')
            return ASK_MENU_ITEM
        
        price = float(price)  # Convert the price to a float

        payers = parts[2:]  # Everything after the price are payers

        # Check if all payers are valid or if 'all' is present
        if "all" in payers:
            payers = users  # If "all" is present, all users will pay
        else:
            invalid_payers = [payer for payer in payers if payer not in users]
            if invalid_payers:
                await update.message.reply_text(f'Payers "{", ".join(invalid_payers)}" not recognized. Please enter valid names or "all".')
                return ASK_MENU_ITEM
        
        # Store the menu item with price and multiple payers
        menu_item = {
            'item': item,
            'price': price,
            'payers': payers  # This is now a list of payers
        }
        menu_data.append(menu_item)
    
    # Display the added menu data
    item_summary = '\n'.join([f'{item["item"]} - {item["price"]} (Payers: {", ".join(item["payers"])})' for item in menu_data])
    await update.message.reply_text(f'Menu items added:\n{item_summary}')
    
    await update.message.reply_text('If you\'re done, type /done to finish and see the summary. If you want to add more items, send them in the same format.')
    return ASK_MENU_ITEM  # Allow them to add more items

# End the conversation when the user is done adding items
async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payer_totals = {}

    for item in menu_data:
        price = item["price"]
        payers = item["payers"]

        if len(payers) > 1:
            split_price = price / len(payers)
        else:
            split_price = price
        
        for payer in payers:
            if payer in payer_totals:
                payer_totals[payer] += split_price
            else:
                payer_totals[payer] = split_price

    # Create the summary for each item
    item_summary = '\n'.join([f'{item["item"]} - {item["price"]} (Payers: {", ".join(item["payers"])})' for item in menu_data])

    # Create the summary of how much each payer owes
    total_summary = '\n'.join([f'{payer} owes: {total:.2f}' for payer, total in payer_totals.items()])

    # Send the final summary to the user
    await update.message.reply_text(f"Here's the final summary:\n{item_summary}\n\nTotal per payer:\n{total_summary}")

    return ConversationHandler.END  # End the conversation

# Fallback handler for cancellation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Conversation canceled.")
    await update.message.reply_text('Conversation canceled.')
    return ConversationHandler.END  # End the conversation

# Help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("/help command was called")
    help_message = (
        "/cancel - Cancel the current calculation\n"
        "/done - Finish and get the summary of the calculation\n"
        "/help - Ask for command list"
    )
    await update.message.reply_text(help_message)
    return ConversationHandler.END

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            ASK_NAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_user)],  # Expect user names
            ASK_MENU_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_menu)],  # Expect full menu input
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('done', end_conversation)]
    )

    # Add the /help command handler
    app.add_handler(CommandHandler('help', help))
    app.add_handler(conversation_handler)

    app.run_polling(poll_interval=1)
