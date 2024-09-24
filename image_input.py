# import pytesseract
# from PIL import Image
# import requests
# from io import BytesIO

# menu_data = []

# async def process_image_input(update, context):
#     global menu_data

#     # Get the image file and convert it to text using OCR
#     photo_file = await update.message.photo[-1].get_file()
#     photo_url = photo_file.file_path
#     response = requests.get(photo_url)
#     img = Image.open(BytesIO(response.content))
    
#     # Extract text from the image
#     extracted_text = pytesseract.image_to_string(img)

#     # Process the extracted text
#     await process_extracted_text(update, context, extracted_text)

# # Function to process text extracted from image as menu items
# async def process_extracted_text(update, context, extracted_text):
#     global menu_data
#     users = context.user_data.get('users', [])

#     # Split the extracted text into lines and process it
#     entries = extracted_text.split('\n')
#     for entry in entries:
#         if not entry.strip():
#             continue
#         try:
#             item, price, payers = entry.split(',')[0].strip(), entry.split(',')[1].strip(), entry.split(',')[2:]
#             payers = [payer.strip() for payer in payers]
#         except ValueError:
#             await update.message.reply_text(f'Invalid format in extracted text for entry: {entry}.')
#             continue

#         # Validate price as a number
#         if not price.replace('.', '', 1).isdigit():
#             await update.message.reply_text(f'Invalid price for entry: {entry}.')
#             continue

#         price = float(price)

#         # Check if payers are valid
#         if 'all' in payers:
#             payers = users
#         elif not all(payer in users for payer in payers):
#             await update.message.reply_text(f'Some payers are not recognized in entry: {entry}.')
#             continue

#         # Add the menu item to the list
#         menu_item = {
#             'item': item,
#             'price': price,
#             'payers': payers
#         }
#         menu_data.append(menu_item)

#     # Display the added items
#     item_summary = '\n'.join([f'{item["item"]} - {item["price"]} (Payers: {", ".join(item["payers"])})' for item in menu_data])
#     await update.message.reply_text(f'Menu items extracted:\n{item_summary}')
#     await update.message.reply_text('If you\'re done, type /done to finish or upload another receipt.')
