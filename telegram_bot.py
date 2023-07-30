#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=unused-argument, wrong-import-position
"""
O diciobot consulta o [Dicio - Dicionário Online de Português],
composto por definições, significados, exemplos e rimas
que caracterizam mais de 400.000 palavras e verbetes.
"""
import logging
from dicio import *
from os import getenv
from dotenv import load_dotenv
from telegram import constants, Update, __version__ as TG_VER
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
load_dotenv()

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}."
        f"Visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

LOG_LEVEL = logging.INFO
BOT_ID = getenv('TELEGRAM_BOT_ID')
SHORT_CMD = ["h", "d", "s", "a", "e", "c", "r", "ana", "t"]
LONG_CMD = [
    "fallback", "start", "ajuda",
    "help", "definir", "sinonimos",
    "antonimos", "exemplos", "conjugar",
    "rimas", "anagramas", "tudo",
    "dia", "hoje"
]
CMD_DICT = {
    "fallback": "fallback",
    "start": "start",
    "help": "help",
    "ajuda": "help",
    "hoje": "dia",
    "dia": "dia",
    "definir": "definir",
    "d": "definir",
    "hoje": "hoje",
    "h": "hoje",
    "sinonimos": "sinonimos",
    "s": "sinonimos",
    "antonimos": "antonimos",
    "a": "antonimos",
    "exemplos": "exemplos",
    "e": "exemplos",
    "conjugar": "conjugar",
    "c": "conjugar",
    "rimas": "rimas",
    "r": "rimas",
    "anagramas": "anagramas",
    "ana": "anagramas",
    "tudo": "tudo",
    "t": "tudo",
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=LOG_LEVEL
)
logging.getLogger("httpx").setLevel(logging.WARNING)


def logHandler(update: Update) -> None:
    if not update:
        return

    log = f"[{update.message.chat.type}]"
    command = 'fallback'

    if update.message.text.startswith("/"):
        split = BOT_ID if BOT_ID in update.message.text else " "
        [cmd, *_] = update.message.text.split(split, 1)
        if cmd.lower().replace("/", "") in CMD_DICT:
            command = CMD_DICT[cmd.lower().replace("/", "")]

    if len(update.message.text) > 0:
        log += f": {update.message.text}"

    logging.getLogger(command).log(LOG_LEVEL, log)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if not update:
        return

    logHandler(update)

    reply = f"Bem vindo ao @diciobot!\nVamos começar?\n\n{ajuda()}"
    if update.message.chat.type == constants.ChatType.PRIVATE:
        reply += f"\n\n{dica()}"
    await update.message.reply_markdown(reply)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    if not update:
        return

    logHandler(update)

    reply = ajuda()
    if update.message.chat.type == constants.ChatType.PRIVATE:
        reply += f"\n\n{dica()}"

    await update.message.reply_markdown(ajuda())


async def dia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update:
        return

    logHandler(update)

    await update.message.reply_markdown(
        buscarPalavraDoDia(),
        disable_web_page_preview=True
    )


async def definir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update:
        return

    logHandler(update)

    await update.message.reply_markdown(
        buscarDefinicao(update.message.text.split(' ')[1]),
        disable_web_page_preview=True
    )


async def sinonimos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def antonimos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def exemplos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def conjugar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def rimas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def anagramas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def tudo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update:
        return

    logHandler(update)

    words = update.message.text.split(',')
    for word in words:
        await update.message.reply_markdown(
            buscarDefinicao(word.strip().lower()),
            disable_web_page_preview=True
        )


def main() -> None:
    """Start the bot."""

    # Create the app and pass the bot's token.
    app = Application.builder().token(getenv('TELEGRAM_TOKEN')).build()

    # Help Command handlers
    app.add_handler(CommandHandler(["start"], start))
    app.add_handler(CommandHandler(["ajuda", "help", "h"], help))

    # Function Command handlers
    app.add_handler(CommandHandler(["dia", "hoje"], dia))
    app.add_handler(CommandHandler(["definir", "d"], definir))
    app.add_handler(CommandHandler(["sinonimos", "s"], sinonimos))
    app.add_handler(CommandHandler(["antonimos", "a"], antonimos))
    app.add_handler(CommandHandler(["exemplos", "e"], exemplos))
    app.add_handler(CommandHandler(["conjugar", "c"], conjugar))
    app.add_handler(CommandHandler(["rimas", "r"], rimas))
    app.add_handler(CommandHandler(["anagramas", "ana"], anagramas))
    app.add_handler(CommandHandler(["tudo", "t"], tudo))

    # Fallback handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
