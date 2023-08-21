from logging import LogRecord, Handler
import telebot


class TelegramBotHandler(Handler):
    def __init__(self, token: str, chat_id: str) -> None:
        super().__init__()
        self.token = token
        self.chat_id = chat_id

    def emit(self, record: LogRecord) -> None:
        bot = telebot.TeleBot(self.token)
        bot.send_message(
            self.chat_id,
            self.format(record)
        )
