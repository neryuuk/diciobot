#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

"""
O diciobot consulta o [Dicio - Dicionário Online de Português],
composto por definições, significados, exemplos e rimas
que caracterizam mais de 400.000 palavras e verbetes.
"""
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import ForceReply, Update, __version__ as TG_VER
from lxml import html
from urllib import request, parse
import logging
import requests
import json

BASE_URL = "https://www.dicio.com.br"

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
        helpMessage = "\n".join([
            "As opções *disponíveis* são as _seguintes_:",
            "",
            "/definir ou /d - *definição* de um _verbete_",
            "/sinonimos ou /s - *sinônimos* de um _verbete_",
            "/antonimos ou /a - *antônimos* de um _verbete_",
            "/exemplos ou /e - *exemplos* de utilização de um _verbete_",
            "/conjugar ou /c - *conjugar* um _verbo_",
            "/rimas ou /r - *rimas* de um _verbete_",
            "/anagramas ou /ana - *anagramas* de um _verbete_",
            "/tudo ou /t - *todas* as opções *disponíveis* de um _verbete_",
            "/dia - *Palavra do dia*."
        ])
        await update.message.reply_markdown(helpMessage)


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


def buscarPalavraDoDia():
    pagina = request.urlopen(BASE_URL)
    tree = html.fromstring(str(pagina.read(), "utf-8"))
    doDia = tree.xpath("//*[@class='word-link']/text()")[0]
    content = "*Palavra do dia:* _{}_\n\n{}".format(
        doDia, buscarDefinicao(doDia)
    )
    return content


def buscarDefinicao(verbete):
    pagina, tree, sugestao = buscar(verbete)

    if pagina.code == 404:
        return quatroZeroQuatro(verbete, sugestao)

    if tree is None:
        return ''

    fonte = "\n*Fonte:* " + pagina.url.replace("_", "\_")
    titulos = tree.xpath('//h2[@class="tit-section"]/text()')
    titulo = ""
    for each in titulos:
        if 'Definição' in each:
            titulo = each.split(' ')

    mensagem = ''
    if len(titulo) != 0:
        mensagem += "*{}* _{}_\n".format(" ".join(titulo[:-1]), titulo[-1])
        definicao = tree.xpath('//p[@class="adicional"]//node()')
        for each in definicao:
            if type(each) == html.HtmlElement:
                if each.tag == "br":
                    mensagem += "\n"
            else:
                mensagem += each.strip().replace(":", ": ")
        mensagem += "\n"

    titulos = tree.xpath('//h2[@class="tit-significado"]/text()')
    if (len(titulos) + len(mensagem)) == 0:
        return "_O verbete_ *{}* _não tem definição ou significado disponíveis._".format(verbete)
    elif len(titulos) == 0:
        mensagem += "Significado: Não encontrado."
        return mensagem.replace("\n ", "\n") + fonte

    titulo = ""
    for each in titulos:
        if 'Significado' in each:
            titulo = each.split(' ')
    mensagem += "*{}* _{}_\n".format(" ".join(titulo[:-1]), titulo[-1])
    for each in tree.xpath('//p[@itemprop="description"]/span'):
        if type(each) == html.HtmlElement:
            if "cl" in each.classes:
                mensagem += each.text_content().strip().replace("*", "\*") + "\n"
            elif "tag" in each.classes:
                mensagem += each.text_content().strip().replace("*", "\*")
            else:
                mensagem += each.text_content().strip().replace("*", "\*") + "\n"
        else:
            mensagem += each.strip() + "\n"

    return mensagem.replace("\n ", "\n").replace("[", "\[") + fonte


def buscar(verbete):
    try:
        busca = request.urlopen("".join([
            BASE_URL,
            "/pesquisa.php?",
            parse.urlencode({'q': verbete})
        ]))
    except requests.exceptions.TooManyRedirects:
        pass

    tree = html.fromstring(str(busca.read(), "utf-8"))
    if "/pesquisa.php" not in busca.url:
        return busca, tree, ""

    # Retornou uma página de busca
    pagina = tree.xpath('//div[@class="found"]')
    if len(pagina) == 0:
        # Não encontrou resultados pra busca do verbete
        pagina = tree.xpath('//div[@id="enchant"]')
        if len(pagina) == 0:
            # Não tem nenhuma sugestao para o verbete nao encontrado
            return requests.get(BASE_URL + "/404"), None, ""

        # Tem sugestões para o verbete não encontrado
        sugestao = pagina[0].text
        return requests.get(BASE_URL + "/404"), None, sugestao

    # Encontrou resultados pra busca do verbete
    pagina = tree.xpath('//a[@class="_sugg"]')
    for each in pagina:
        content = each.xpath('span[@class="list-link"]/text()')
        # Encontrou o verbete solicitado nos resultados
        if content and content[0] and (content[0] == verbete):
            busca = request.urlopen(BASE_URL + each.attrib["href"])
            tree = html.fromstring(str(busca.read(), "utf-8"))
            return busca, tree, ""

    # Não encontrou o verbete solicitado nos resultados
    busca = request.urlopen(BASE_URL + "/404")
    tree = html.fromstring(str(busca.read(), "utf-8"))
    return busca, tree, sugestao


def quatroZeroQuatro(verbete, sugestao, verbo=False):
    naoEncontrado = "_O {}_ *{}* _não foi encontrado._".format(
        "verbo" if verbo else "verbete",
        verbete
    )

    if len(sugestao) == 0:
        return naoEncontrado

    naoEncontrado += "\n\n_Você quis dizer_ *{}*?".format(sugestao)
    return naoEncontrado


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
