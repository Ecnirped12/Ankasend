import os
from telegram import Update
import telegram
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
)
from telegram.constants import ParseMode
from bot.extractor.sms_details import SMSDetails
from bot.sender_engine.anka_sender_eng import AnkarexSender
from telegram.request import HTTPXRequest

class SMSSenderBot:

    def __init__(self, access_token: str) -> None:

        self.request = HTTPXRequest(
            connect_timeout=20, read_timeout=30, write_timeout=30, pool_timeout=10, http_version="1.1",
        )

        self.application = ApplicationBuilder().token(access_token).request(self.request).build()
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(MessageHandler(filters.TEXT, self.sms_contents))


    def reply_message(self, update: Update, message: str) -> None:
        return update.message.reply_text(message, parse_mode=ParseMode.HTML)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self.reply_message(update, f'welcome @{update.effective_user.username}')

    async def sms_contents(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        content = update.message.text

        sms_details = SMSDetails(content)
        details_response = sms_details.sms_details_composer()

        if details_response == 'Not Found':
            self.reply_message()
        else:
            anka_sender_engine = AnkarexSender(details_response)
            response_data =  anka_sender_engine.send_sms()

            if response_data == 'blacklisted':
                await self.reply_message(update, f'<b>Error occur:</b> The number is blacklisted')
            elif response_data['info'] == 'QUEUED':
                await self.reply_message(update,
            f"""
<b>SMS Accepted</b>

<b>Status</b>: <b>SENT</b>
<b>Batch ID</b>: <code>{response_data['batch_id']}</code>
<b>Recipients</b>: {response_data['numbers_count']}
<b>Cost</b>: ${response_data['estimated_cost']}
<b>Balance</b>: ${response_data['balance']}
                """
                    )
            else:
                await self.reply_message(update, f'<b>Error occur:</b> {response_data['info']}')

    def run_bot(self) -> None:
        try:
            print('Start start')
            self.application.run_polling()
        except telegram.error.TimedOut:
            print('Timeout error occurred. Retrying...')

