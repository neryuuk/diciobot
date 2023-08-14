#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=unused-argument, wrong-import-position
"""
O diciobot consulta o [Dicio - Dicionário Online de Português],
composto por definições, significados, exemplos e rimas
que caracterizam mais de 400.000 palavras e verbetes.
"""
import dicio
import html
import json
import logging
from dotenv import load_dotenv
from os import getenv
from telegram import Update, __version__ as TG_VER
from telegram.constants import ParseMode, ChatType
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler
from telegram.ext.filters import COMMAND, TEXT
from traceback import format_exception

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
CHAT_ID = getenv('CHAT_ID')
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


def isValid(update: Update) -> bool:
    if not update:
        return False
    if not update.message:
        return False
    if not update.message.text:
        return False
    return True


def isPrivate(update: Update) -> bool:
    return update.message.chat.type == ChatType.PRIVATE


def command(update: Update) -> str:
    cmd = 'fallback'

    if isValid(update) and update.message.text.startswith("/"):
        split = BOT_ID if BOT_ID in update.message.text else " "
        [cmd, *_] = update.message.text.lower().replace("/", "").split(split, 1)

    if cmd in CMD_DICT:
        return CMD_DICT[cmd]
    else:
        return 'fallback'


def logHandler(update: Update) -> None:
    if not isValid(update):
        return
    identity = [str(update.message.chat.type)]
    if not isPrivate(update):
        identity.append(str(update.message.chat.id))
    identity.append(str(update.message.from_user.id))
    identity.append(str(update.message.from_user.username))

    log = f'[{",".join(identity)}]'

    if len(update.message.text) > 0:
        log += f": {update.message.text}"

    logging.getLogger(command(update)).log(LOG_LEVEL, log)


async def start(update: Update, _) -> None:
    if not isValid(update):
        return

    logHandler(update)
    reply = f"Bem vindo ao @diciobot!\nVamos começar?\n\n{dicio.ajuda()}"
    if isPrivate(update):
        reply += f"\n\n{dicio.dica()}"

    await update.message.reply_markdown(reply)


async def help(update: Update, _) -> None:
    if not isValid(update):
        return

    logHandler(update)
    reply = dicio.ajuda()
    if isPrivate(update):
        reply += f"\n\n{dicio.dica()}"

    await update.message.reply_markdown(dicio.ajuda())


async def dia(update: Update, _) -> None:
    if not isValid(update):
        return

    logHandler(update)
    await update.message.reply_markdown(
        dicio.dia(),
        disable_web_page_preview=True,
    )


async def handler(method: callable, update: Update) -> None:
    if not isValid(update):
        return

    logHandler(update)
    for resultado in dicio.buscar(update.message.text, method):
        await update.message.reply_markdown(resultado, True)


async def definir(update: Update, _) -> None:
    await handler(dicio.definir, update)


async def sinonimos(update: Update, _) -> None:
    await handler(dicio.sinonimos, update)


async def antonimos(update: Update, _) -> None:
    await handler(dicio.antonimos, update)


async def exemplos(update: Update, _) -> None:
    await handler(dicio.exemplos, update)


async def conjugar(update: Update, _) -> None:
    await handler(dicio.conjugar, update)


async def rimas(update: Update, _) -> None:
    await handler(dicio.rimas, update)


async def anagramas(update: Update, _) -> None:
    await handler(dicio.anagramas, update)


async def tudo(update: Update, _) -> None:
    await handler(dicio.tudo, update)


async def fallback(update: Update, _) -> None:
    if not isValid(update):
        return

    if not isPrivate(update):
        return

    logHandler(update)
    words = update.message.text.split(',')
    for word in words:
        if not word or not word.strip():
            continue

        await update.message.reply_markdown(
            dicio.buscar(f"/d {word.strip().lower()}", dicio.definir)[0],
            disable_web_page_preview=True,
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.getLogger(command(update)).error(
        "Exception while handling an update",
        # exc_info=context.error
    )

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    await iterateError(
        html.escape(json.dumps(update_str, indent=2, ensure_ascii=False)),
        context
    )

    tb_str = "".join(format_exception(
        None, context.error, context.error.__traceback__
    ))
    await iterateError(html.escape(tb_str), context)


async def iterateError(content: str, context: ContextTypes.DEFAULT_TYPE, start: int = 0):
    MAX_LEN = 4000

    await context.bot.send_message(CHAT_ID, f"<pre>{content[start:start + MAX_LEN]}</pre>", ParseMode.HTML)
    if len(content[start:]) > MAX_LEN:
        await iterateError(content, context, start + MAX_LEN)


def main() -> None:
    app = Application.builder().token(getenv('TELEGRAM_TOKEN')).build()

    app.add_handler(CommandHandler(["start"], start))
    app.add_handler(CommandHandler(["ajuda", "help", "h"], help))
    app.add_handler(CommandHandler(["dia", "hoje"], dia))
    app.add_handler(CommandHandler(["definir", "d"], definir))
    app.add_handler(CommandHandler(["sinonimos", "s"], sinonimos))
    app.add_handler(CommandHandler(["antonimos", "a"], antonimos))
    app.add_handler(CommandHandler(["exemplos", "e"], exemplos))
    app.add_handler(CommandHandler(["conjugar", "c"], conjugar))
    app.add_handler(CommandHandler(["rimas", "r"], rimas))
    app.add_handler(CommandHandler(["anagramas", "ana"], anagramas))
    app.add_handler(CommandHandler(["tudo", "t"], tudo))

    app.add_handler(MessageHandler(TEXT & ~COMMAND, fallback))
    app.add_error_handler(error_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
