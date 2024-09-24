from telegram.ext import ConversationHandler

menu_data = []  # Initialize an empty list to store menu items

# Function to handle manual input of menu items
async def handle_manual_input(update, context):
    global menu_data
    users = context.user_data.get('users', [])
    
    # Expecting user to provide input in the format: "Item, Price, Payer1, Payer2"
    entries = update.message.text.split(';')  # Split input into multiple items using ';'
    
    # Iterate over each item entry
    for entry in entries:
        entry_parts = entry.split(',')  # Split each entry by commas

        # Validate that the input contains at least item and price
        if len(entry_parts) < 2:
            await update.message.reply_text(f'Invalid format for entry: {entry}. Please use the format "Item, Price, Payer".')
            continue
        
        try:
            # Extract item and price
            item, price = entry_parts[0].strip(), entry_parts[1].strip()
            # Extract payers, can be empty if not provided
            payers = [payer.strip() for payer in entry_parts[2:]]  # Payers can be optional

            # Ensure price is a valid number
            if not price.replace('.', '', 1).isdigit():
                await update.message.reply_text(f'Invalid price for entry: {entry}. Please enter a valid number for the price.')
                continue

            # Convert price to a floating-point number
            price = float(price)

            # Check if payers are valid (if provided)
            if payers:
                if 'all' in payers:
                    payers = users  # If 'all', include all users
                elif not all(payer in users for payer in payers):
                    await update.message.reply_text(f'Some payers are not recognized in entry: {entry}.')
                    continue
            else:
                await update.message.reply_text('Please enter at least one payer or "all".')
                continue

            # Add the menu item to the list
            menu_item = {
                'item': item,
                'price': price,
                'payers': payers
            }
            menu_data.append(menu_item)

        except ValueError:
            await update.message.reply_text(f'Invalid format for entry: {entry}. Please use the format "Item, Price, Payer".')

    # Show the summary of added items
    item_summary = '\n'.join([f'{item["item"]} - {item["price"]} (Payers: {", ".join(item["payers"])})' for item in menu_data])
    await update.message.reply_text(f'Menu items added:\n{item_summary}')

    # Ask if they want to finish or add more
    await update.message.reply_text('If you\'re done, type /done to finish or send more items in the same format.')

# Function to handle the end of the conversation
async def handle_done(update, context):
    global menu_data
    users = context.user_data.get('users', [])

    # Calculate totals for each payer
    payer_totals = {}

    for item in menu_data:
        payers = item['payers']
        price = item['price']

        # Split price among all payers if 'all' was used
        if 'all' in payers:
            split_price = price / len(users)
            for user in users:
                payer_totals[user] = payer_totals.get(user, 0) + split_price
        else:
            split_price = price / len(payers)
            for payer in payers:
                payer_totals[payer] = payer_totals.get(payer, 0) + split_price

    # Generate final summary
    total_summary = '\n'.join([f'{payer} owes: {total:.2f}' for payer, total in payer_totals.items()])
    await update.message.reply_text(f"Here's the final summary of what each person owes:\n{total_summary}")

    # Reset menu data
    menu_data = []
    
    # End the conversation
    return ConversationHandler.END  # End the conversation
