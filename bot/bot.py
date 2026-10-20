import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
)
from dotenv import load_dotenv
from telegram.constants import ParseMode
from bot.extractor.sms_details import SMSDetails
from bot.sender_engine.anka_sender_eng import AnkarexSender
from telegram.request import HTTPXRequest

load_dotenv()

class SMSSenderBot(AnkarexSender, SMSDetails):

    def __init__(self, access_token: str) -> None:
        self.api_key = os.getenv('API_KEY')
        self.api = os.getenv('API')
        self.request = HTTPXRequest(
            connect_timeout=20, read_timeout=30, write_timeout=30, pool_timeout=10, http_version="1.1",
        )
        self.content: str = ""
        self.keyboard = []
        self.row = []
        self.sms_detail = None
        self.application = ApplicationBuilder().token(access_token).request(self.request).build()
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(MessageHandler(filters.TEXT, self.sms_contents))
        self.application.add_handler(CallbackQueryHandler(self.handle_routes_button))
        super().__init__()

    def reply_message(self, update: Update, message: str) -> None:
        target = update.effective_message
        if target:
            return target.reply_text(
                message,
                parse_mode=ParseMode.HTML
            )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self.reply_message(update, f'welcome @{update.effective_user.username}')

    async def sms_contents(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.content = update.message.text
        self.sms_detail = self.sms_details_composer()

        context.user_data["message_contents"] = self.sms_detail

        if self.sms_detail == 'Not Found':
             await self.reply_message(
                update,
                "Unable to identify the SMS details."
            )
        else:
            self.serve_routes_worker()
            # fetch_available_routes from MessageParge
            if self.route_found:
                channels = self.fetch_available_routes()
                context.user_data["route_options"] = channels
                keyboard = [
                    [InlineKeyboardButton( "All Route", callback_data=f"All Route")]
                ]
                row = []
                for channel in channels:
                    row.append(
                        InlineKeyboardButton( channel["channel"], callback_data=channel["option_id"])
                    )
                    if len(row) == 2:
                        keyboard.insert(0, row)
                        row = []
                if (row):
                    keyboard.insert(0, row)

                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    (
                        f"<b>SELECT FROM AVAILABLE ROUTES</b>\n\n"
                        f"<b>PHONE NUMBER:</b> <code>{self.sms_detail["phone_number"]}</code>\n\n"
                        f"<b>MESSAGE:</b> <code>{self.sms_detail["message"]}</code>"
                    ), reply_markup=reply_markup, parse_mode=ParseMode.HTML
                )
            else:
                match self.response_title:
                    case "blacklisted":
                        await self.reply_message(update, f'<b>Error occur:</b> The number is blacklisted')
                    case "data":
                        if self.sender_response['data']["status"] == 'queued':
                            await self.reply_message(update, "Message sent with random route_option")
                    case "error":
                        response = self.sender_response["error"]
                        await self.reply_message(update, (
                            f'<b>ERROR STATUS:</b> {response["code"]}\n'
                            f'<b>ERROR MESSAGE: </b> {response["message"]}\n'
                            f'<b>ERROR DETAIL: </b> {response["detail"]}'
                        ))
                    case _:
                        print("Found")
                        pass
    async def handle_routes_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        print("Processing")

        sms_contents = context.user_data.get("message_contents", "")
        channels = context.user_data.get("route_options", "")

        if (query.data):
            routes_id_list = [query.data] if query.data != "All Route" else  [channel["option_id"] for channel in channels]

            for route_id in routes_id_list:
                self.send_message(route_id, sms_contents)
                match self.response_title:
                    case "blacklisted":
                        await self.reply_message(update, f'<b>Error occur:</b> The number is blacklisted')
                    case "data":
                        if self.sender_response['data']["status"] == 'queued':
                            message = (
                                f"<b>SMS Accepted</b>\n"
                                f"<b>Status</b>: <b>SENT</b>\n"
                                f"<b>Batch ID</b>: <code>{self.sender_response['data']['batch_id']}</code>\n"
                                f"<b>Recipients </b>: {self.sender_response['data']['sender_ids_effective'][0]['recipients']}\n"
                                f"<b>Cost</b>: ${self.sender_response['data']['estimated_cost']}\n"
                            )
                            await self.reply_message(update, message)
                    case "error":
                        response = self.sender_response["error"]["fields"][0]["message"]
                        await self.reply_message(update, f'<b>Error occur:</b> {response}')
                    case _:
                        print("Found")
                        pass
        else:
            print("Query_value", query.data)

    def run_bot(self) -> None:
        try:
            print('Start start')
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        except telegram.error.TimedOut:
            print('Timeout error occurred. Retrying...')

