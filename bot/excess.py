async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [KeyboardButton("/Help")],
        [KeyboardButton("/Price")],
        [KeyboardButton("/Request_count")],
    ]

    await update.message.reply_text(
        """
        **Bot Commands:**

        * **Help** - Displays this help message.
        * **Price** - Gets the price of a pair.
        * **Request_count** - Displays the total number of requests.
        """,
         reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True),
    )


    async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the contract address:")
    return 1

async def get_contract_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contract_address = update.message.text
    await get_pair_data(update, context, contract_address)
    return ConversationHandler.END


async def get_pair_data(update, context, pair_address):
    chain_id = 'solana'
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_address}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            await bot_send_text(update, context, "Error: " + data['error'])
            return

        pair_data = data.get('pair')
        if pair_data:
            txns_h24 = pair_data.get('txns', {}).get('h24')
            pair_symbol = pair_data.get('baseToken', {}).get('symbol')

            # Send a response message to Telegram
            message = f"Pair Data:\n"
            message += f"Symbol: {pair_symbol}\n"
            message += f"Price (USD): {pair_data.get('priceUsd')}\n"
            message += f"Transactions (24h): {txns_h24.get('buys') + txns_h24.get('sells')}\n"
            await bot_send_text(update, context, message)
        else:
            await bot_send_text(update, context, "Pair data not found")
            return

    except requests.exceptions.RequestException as e:
        await bot_send_text(update, context, "An error occurred while making the request. Please try again later.")


 price_handler = ConversationHandler(
        entry_points=[CommandHandler('Price', price_command)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contract_address)],
        },
        fallbacks=[],
    )
    

app.add_handler(CommandHandler('help', help_command))
app.add_handler(CommandHandler('price', price_command))
app.add_handler(price_handler)
