#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unused-argument, wrong-import-position

"""
O diciobot consulta o [Dicio - Dicionário Online de Português],
composto por definições, significados, exemplos e rimas
que caracterizam mais de 400.000 palavras e verbetes.
"""
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import ForceReply, Update, __version__ as TG_VER
import logging
import json
from dicio import *

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.INFO)
logger = logging.getLogger(__name__)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    if update and update.message:
        await update.message.reply_markdown(ajuda())


async def dia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (update and update.message):
        await update.message.reply_markdown(
            buscarPalavraDoDia(),
            disable_web_page_preview=True
        )


async def definir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (update and update.message and update.message.text):
        await update.message.reply_markdown(
            buscarDefinicao(update.message.text.split(' ')[1]),
            disable_web_page_preview=True
        )


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (update and update.message and update.message.text):
        words = update.message.text.split(',')
        for word in words:
            await update.message.reply_markdown(
                buscarDefinicao(word.strip().lower()),
                disable_web_page_preview=True
            )


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    with open('config.json') as config_file:
        config = json.load(config_file)
    app = Application.builder().token(config["Telegram"]["token"]).build()

    # on different commands - answer in Telegram
    app.add_handler(CommandHandler(["start", "ajuda", "help", "h"], help))
    app.add_handler(CommandHandler(["definir", "d"], definir))
    app.add_handler(CommandHandler(["sinonimos", "s"], help))
    app.add_handler(CommandHandler(["antonimos", "a"], help))
    app.add_handler(CommandHandler(["exemplos", "e"], help))
    app.add_handler(CommandHandler(["conjugar", "c"], help))
    app.add_handler(CommandHandler(["rimas", "r"], help))
    app.add_handler(CommandHandler(["anagramas", "ana"], help))
    app.add_handler(CommandHandler(["tudo", "t"], help))
    app.add_handler(CommandHandler(["dia", "hoje"], dia))

    # on non command i.e message - echo the message on Telegram
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
