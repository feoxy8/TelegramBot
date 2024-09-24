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
    await update.message.reply_text('Hello! Please enter names separated by hypen(-).')
    return ASK_NAMES  # Move to the state where bot expects user to input names

# Handler to capture user's names
async def input_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Entered input_user handler")  # Log to ensure this handler is reached
    
    global users
    users = update.message.text.split(' ')  # Split the names by '-'
    users = [name.strip() for name in users]  # Remove any extra whitespace around each name
    num = len(users)
    logger.info(f"Received names: {users}, Number of people: {num}")
    
    if num > 1:
        name_list = "\n".join(users)  # Format the names nicely for display
        await update.message.reply_text(f'Nice to meet all of you:\n{name_list}')
    else:
        await update.message.reply_text(f'Nice to meet you, {users[0]}!')
    
    await update.message.reply_text("Let's start adding menu items. What's the first menu item?")
    return ASK_MENU_ITEM  # Move to next state to ask for menu item

# Handler to capture menu item name
async def ask_menu_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_item'] = update.message.text  # Store menu item name
    await update.message.reply_text(f'You entered {context.user_data["current_item"]}. What\'s the price for this item?')
    return ASK_PRICE  # Move to next state to ask for price

# Handler to capture the price
async def ask_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price_text = update.message.text
    if not price_text.replace('.', '', 1).isdigit():  # Ensure it's a valid number
        await update.message.reply_text('Please enter a valid number for the price.')
        return ASK_PRICE

    context.user_data['current_price'] = float(price_text)  # Store price
    await update.message.reply_text('Who will pay for this item? Enter the name or type "all" if everyone shares.')
    return ASK_PAYER  # Move to next state to ask for payer

# Handler to capture who pays
async def ask_payer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payer = update.message.text.strip()
    
    if payer.lower() == 'all':
        context.user_data['payer'] = 'all'
    elif payer in users:
        context.user_data['payer'] = payer
    else:
        await update.message.reply_text(f'User "{payer}" not recognized. Please enter a valid name or "all".')
        return ASK_PAYER  # Ask again if the payer is invalid
    
    # Store the current menu item, price, and payer
    menu_item = {
        'item': context.user_data['current_item'],
        'price': context.user_data['current_price'],
        'payer': context.user_data['payer']
    }
    menu_data.append(menu_item)
    logger.info(f"Added menu item: {menu_item}")
    
    await update.message.reply_text(f'Added: {menu_item["item"]} - {menu_item["price"]} (Payer: {menu_item["payer"]})')
    
    # Ask if they want to add another item
    await update.message.reply_text('Would you like to add another item? If yes, please enter the next item name. If not, type "done".')
    return ASK_MENU_ITEM  # Return to ASK_MENU_ITEM state for next item or finish

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
            ASK_MENU_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_menu_item)],  # Expect menu item
            ASK_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_price)],  # Expect price
            ASK_PAYER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_payer)]  # Expect payer
        },
        fallbacks=[CommandHandler('cancel', cancel), 
                   CommandHandler('done', end_conversation),
                   
                   ]  # Allow canceling or finishing
    )

    # Add the /help command handler
    app.add_handler(CommandHandler('help', help))

    # Add conversation handler to the app
    app.add_handler(conversation_handler)

    # Start the bot
    app.run_polling(poll_interval=1)
